from pathlib import Path

def detect_folder(folder: Path) -> list[Path]:

    folder = Path(folder)

    mp3_files = [f.resolve() for f in folder.glob("*.mp3")]

    print(f"Detected MP3 files: {mp3_files}")

    if not mp3_files:
        raise FileNotFoundError(f"No MP3 files found in {folder}")
    
    return mp3_files