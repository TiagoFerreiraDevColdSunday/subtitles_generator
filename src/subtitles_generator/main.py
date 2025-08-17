import time
import typer
import os

from faster_whisper.tokenizer import _LANGUAGE_CODES
from pathlib import Path
from watchdog.observers import Observer
from thread import Handler

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

app =  typer.Typer()

@app.command()
def call_event(
            language: str = typer.Argument("en", help="Language for subtitles generation"),
            directory: Path = typer.Argument("", help="Directory to watch for new files"),
            file_trigger: str = typer.Argument(".txt", help="Trigger file extension"),
            file_type: str = typer.Argument("mp3", help="Type of file to watch"),
            parallel: bool = typer.Argument(False, help="Use processes to handle multiple files"),
            recursive: bool = typer.Argument(False, help="If events will be emitted for sub-directories traversed recursively")
            )-> None:
    
    # Still doing these checks for user who don't use GUI
    try:
        directory = Path(directory)
        if not directory.exists() or not directory.is_dir():
            raise FileNotFoundError(f"The directory {directory} does not exist or is not a directory.")

        if language not in _LANGUAGE_CODES:
            raise ValueError(f"Language '{language}' is not supported. Available languages: {', '.join(_LANGUAGE_CODES)}")
    except Exception as e:
        print(f"\nError: {e}\n")
        return

    observer = Observer()
    handler = Handler(language=language, directory=directory, file_trigger=file_trigger, file_type=file_type, parallel=parallel)

    observer.schedule(handler, str(directory), recursive=recursive)
    observer.start()

    print(f"Parallel: {parallel}")
    print(f"Waiting for a {file_trigger} to be created on: {directory}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    app()

