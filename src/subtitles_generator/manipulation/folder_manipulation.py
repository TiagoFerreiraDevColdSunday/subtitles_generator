from pathlib import Path

def detect_folder(folder: Path, file_type: str) -> list[Path]:

    folder = Path(folder)

    files = [f.resolve() for f in folder.glob(f"*.{file_type}")]

    print(f"Detected files: {files}")

    if not files:
        raise FileNotFoundError(f"No files with the format {file_type} found in {folder}")
    
    return files