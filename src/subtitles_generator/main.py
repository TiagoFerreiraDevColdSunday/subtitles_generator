import time
import typer
import os

from faster_whisper.tokenizer import _LANGUAGE_CODES
from pathlib import Path
from typing import List, Optional
from watchdog.observers import Observer
from thread import Handler, action
from whisper_functions import generate_subtitles
from manipulation.folder_manipulation import detect_folder

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

app = typer.Typer()


def _validate_language(language: str) -> None:
    if language not in _LANGUAGE_CODES:
        raise ValueError(f"Language '{language}' is not supported. Available languages: {', '.join(_LANGUAGE_CODES)}")


def _validate_directory(directory: Path) -> Path:
    directory = Path(directory)
    if not directory.exists() or not directory.is_dir():
        raise FileNotFoundError(f"The directory {directory} does not exist or is not a directory.")
    return directory


@app.command("watch")
def call_event(
            language: str = typer.Argument("en", help="Language for subtitles generation"),
            directory: Path = typer.Argument("", help="Directory to watch for new files"),
            file_trigger: str = typer.Argument(".txt", help="Trigger file extension"),
            file_type: str = typer.Argument("mp3", help="Type of file to watch"),
            parallel: bool = typer.Argument(False, help="Use processes to handle multiple files"),
            recursive: bool = typer.Argument(False, help="If events will be emitted for sub-directories traversed recursively")
            ) -> None:

    try:
        _validate_language(language)
        directory = _validate_directory(directory)
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


@app.command("select")
def call_select(
            language: str = typer.Argument("en", help="Language for subtitles generation"),
            files: Optional[List[str]] = typer.Argument(None, help="Audio files to process"),
            output_directory: Optional[str] = typer.Argument(None, help="Directory to save subtitles"),
            parallel: bool = typer.Argument(False, help="Use processes to handle multiple files"),
            ) -> None:

    try:
        _validate_language(language)

        if not files:
            raise ValueError("No files provided. Please select at least one audio file.")

        file_paths = [Path(f) for f in files]
        for f in file_paths:
            if not f.exists() or not f.is_file():
                raise FileNotFoundError(f"File not found: {f}")

        if output_directory:
            out_dir = _validate_directory(Path(output_directory))
        else:
            out_dir = file_paths[0].parent

    except Exception as e:
        print(f"\nError: {e}\n")
        return

    print(f"Parallel: {parallel}")
    print(f"Processing {len(file_paths)} file(s)...")
    print(f"Output directory: {out_dir}")

    generate_subtitles(
        audio_files=file_paths,
        language=language,
        directory=str(out_dir),
        parallel=parallel,
    )


if __name__ == "__main__":
    app()

