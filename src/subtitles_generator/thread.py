from pathlib import Path
import threading
from watchdog.events import FileSystemEventHandler
from folder_manipulation import detect_folder
from whisper_functions import generate_subtitles

FOLDER = Path("/Users/tiagoferreira/projects/subtitles-generator/src/subtitles_generator/subtitles")

def action(language: str, directory: str):
    mp3_paths = detect_folder(directory)
    generate_subtitles(audio_files=mp3_paths, language=language,directory=directory)
    

class Handler(FileSystemEventHandler):

    def __init__(self, language: str, directory: str, file_trigger: str):
        super().__init__()
        self.language = language
        self.directory = Path(directory)
        self.file_trigger = file_trigger

    def on_created(self, event):
        path = Path(event.src_path)
        if path.suffix.lower() == self.file_trigger and path.is_file():
            # Run processing in a separate thread so it doesn't block
            threading.Thread(target=action, args=(self.language, self.directory)).start()
