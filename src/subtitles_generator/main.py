import time
import typer
import os

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
                ) -> None:
    observer = Observer()
    handler = Handler(language=language, directory=directory, file_trigger=file_trigger, file_type=file_type, parallel=parallel)

    observer.schedule(handler, str(directory), recursive=False)
    observer.start()

    print(f"Parallel: {parallel}")
    print(f"Watching for new files in: {directory}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    app()

