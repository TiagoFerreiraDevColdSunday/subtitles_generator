
import os


def get_device_and_compute_type() -> tuple[str, str]:
    """Auto-detect the best device and compute type for the current system."""
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda", "float16"
    except ImportError:
        pass
    return "cpu", "int8"

def format_timestamp(seconds: float) -> str:
    # Format seconds to SRT timestamp: HH:MM:SS,mmm
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

def get_subtitle_file_path_name(file_name: str) -> tuple[str, str]:
    """
    Extracts the subtitle file name from the given file name.
    
    Args:
        file_name (str): The name of the file.
        
    Returns:
        str: The extracted subtitle file name.
    """
    splitter = file_name.split("/")

    name = os.path.splitext(splitter[-1])[0]
    path = "/".join(splitter[:-1]) # All elements except the last one (the file name)

    return name, path