import os

from pathlib import Path
from typing import List
from faster_whisper import WhisperModel
from concurrent.futures import ProcessPoolExecutor, as_completed
from manipulation.subtitles_manipulation import style_subtitles 

# try "large-v3-turbo", device="cuda" or device="metal", compute_type="float16"
MODEL = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")

def generate_subtitles(audio_files: List[Path], language: str, directory: str, parallel: bool) -> None:


    if parallel:
        n_workers = len(audio_files)

        with ProcessPoolExecutor(max_workers=n_workers) as ex:
            futures = [ex.submit(_generate_subtitles, audio_file, language, directory) for audio_file in audio_files]

            # Wait for all futures to complete
            for future in as_completed(futures):
                future.result()
    
    else:
        for audio_file in audio_files:
            _generate_subtitles(audio_file, language, directory)

def _generate_subtitles(audio_file: Path, language: str = "en", directory: str = "") -> None:

    file_name = f"{directory}/{audio_file.stem}.srt"
    print(f"Processing file {audio_file.name}\n\nFiles will be sent to {directory}\n\n")

    segments, info = MODEL.transcribe(str(audio_file), language=language)

    # Write SRT manually from faster_whisper segments
    with open(file_name, "w", encoding="utf-8") as f:
        for idx, segment in enumerate(segments):
            # segment.start, segment.end, segment.text
            start = _format_timestamp(segment.start)
            end = _format_timestamp(segment.end)
            text = segment.text.strip().replace("\n", " ")
            f.write(f"{idx+1}\n{start} --> {end}\n{text}\n\n")

    subtitles_name, path = _get_subtitle_file_path_name(file_name)
    style_subtitles(file=file_name, subtitle_name=subtitles_name, path=path)

def _format_timestamp(seconds: float) -> str:
    # Format seconds to SRT timestamp: HH:MM:SS,mmm
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

def _get_subtitle_file_path_name(file_name: str) -> tuple[str, str]:
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
