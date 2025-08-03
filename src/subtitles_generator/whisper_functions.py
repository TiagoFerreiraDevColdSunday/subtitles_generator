from pathlib import Path
from typing import List
import whisper

from whisper.utils import WriteSRT
from manipulation.subtitles_manipulation import style_subtitles 

# try "large-v3-turbo", device="cuda" or device="metal", compute_type="float16"
MODEL = whisper.load_model("large-v3-turbo", device="cpu")

def generate_subtitles(audio_files: List[Path], language: Path = "en", directory: str = "") -> None:
    
    for i, audio_file in enumerate(audio_files):
        
        file_name = f"{directory}/output_{i}.srt"

        print(f"Processing file {audio_file.name}\n\nFiles will be sent to {directory}\n\n")

        result = MODEL.transcribe(str(audio_file), language=language) # ja
        
        write_srt = WriteSRT(output_dir=audio_file.parent)

        with open(file_name, "w", encoding="utf-8") as f:
            write_srt.write_result(result, file=f)

        subtitles_name, path = _get_subtitle_file_path_name(file_name)

        style_subtitles(file=file_name, subtitle_name=subtitles_name, path=path)

def _get_subtitle_file_path_name(file_name: str) -> tuple[str, str]:
    """
    Extracts the subtitle file name from the given file name.
    
    Args:
        file_name (str): The name of the file.
        
    Returns:
        str: The extracted subtitle file name.
    """
    splitter = file_name.split("/")

    name = splitter[-1].replace("", ".srt") 
    path = "/".join(splitter[:-1]) # All elements except the last one (the file name)

    return name, path
