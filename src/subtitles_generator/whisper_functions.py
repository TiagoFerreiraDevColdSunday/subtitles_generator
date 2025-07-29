from pathlib import Path
from typing import List
import whisper

from whisper.utils import WriteSRT

MODEL = whisper.load_model("turbo")

def generate_subtitles(audio_files: List[Path], language: Path = "en", directory: str = "") -> None:
    
    for i, audio_file in enumerate(audio_files):
        
        print(f"Processing file {audio_file.name}\nFiles will be sent to {directory}")

        result = MODEL.transcribe(str(audio_file), language=language) # ja
        
        write_srt = WriteSRT(output_dir=audio_file.parent)

        with open(f"{directory}/output_{i}.srt", "w", encoding="utf-8") as f:
            write_srt.write_result(result, file=f)