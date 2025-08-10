from pathlib import Path
import time
import typer
import os

from watchdog.observers import Observer
from thread import Handler

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
app =  typer.Typer()

@app.command()
def call_thread(language: str, directory: str, file_trigger: str, file_type : str = "mp3"):
    observer = Observer()
    handler = Handler(language=language, directory=directory, file_trigger=file_trigger, file_type=file_type)

    observer.schedule(handler, str(directory), recursive=False)
    observer.start()

    print(f"Watching for new files in: {directory}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    app()

