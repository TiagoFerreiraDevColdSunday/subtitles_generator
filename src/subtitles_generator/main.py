from pathlib import Path
import time
import typer

from watchdog.observers import Observer
from thread import Handler

app =  typer.Typer()

@app.command()
def call_thread(language: str, directory: str, file_trigger: str):
    observer = Observer()
    handler = Handler(language=language, directory=directory, file_trigger=file_trigger)

    observer.schedule(handler, str(directory), recursive=False)
    observer.start()

    print(f"Watching for new .mp3 files in: {directory}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    app()

