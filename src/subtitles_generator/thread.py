from pathlib import Path
from watchdog.events import FileSystemEventHandler
from manipulation.folder_manipulation import detect_folder
from whisper_functions import generate_subtitles

def action(language: str, directory: str, file_type, parallel: bool):
    
    try:
        mp3_paths = detect_folder(directory, file_type)
    except FileNotFoundError as e:
        print(f"\nInfo: {e}")
        return
    
    generate_subtitles(audio_files=mp3_paths, language=language,directory=directory,parallel=parallel)
    

class Handler(FileSystemEventHandler):
    def __init__(self, language: str, directory: str, file_trigger: str, file_type: str, parallel: bool):
        super().__init__()
        self.language = language
        self.directory = Path(directory)
        self.file_trigger = file_trigger
        self.file_type = file_type
        self.parallel = parallel

    def on_created(self, event):
        path = Path(event.src_path)
        if path.suffix.lower() == self.file_trigger and path.is_file():
            action(self.language, self.directory, self.file_type, self.parallel)
