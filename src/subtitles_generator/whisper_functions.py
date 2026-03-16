import os

from pathlib import Path
from typing import List
from faster_whisper import WhisperModel
from concurrent.futures import ProcessPoolExecutor, as_completed
from manipulation.subtitles_manipulation import style_subtitles
from utils import get_device_and_compute_type, format_timestamp, get_subtitle_file_path_name


_device, _compute_type = get_device_and_compute_type()
MODEL = WhisperModel("large-v3-turbo", device=_device, compute_type=_compute_type)

_MAX_WORKERS = min(os.cpu_count() or 1, 4) # 4 max workers to avoid overwhelming the system, adjust as needed


def generate_subtitles(audio_files: List[Path], language: str, directory: str, parallel: bool) -> None:
    """Generate SRT subtitles for each audio file, optionally in parallel."""
    if parallel:
        n_workers = min(len(audio_files), _MAX_WORKERS)

        with ProcessPoolExecutor(max_workers=n_workers) as ex:
            futures = [ex.submit(_generate_subtitles, audio_file, language, directory) 
                       for audio_file in audio_files]

            # Wait for all futures to complete
            for future in as_completed(futures):
                try:
                    future.result()
                except (OSError, RuntimeError) as e:
                    print(f"Error in worker process: {e}")
    else:
        for audio_file in audio_files:
            _generate_subtitles(audio_file, language, directory)

def _generate_subtitles(audio_file: Path, language: str = "en", directory: str = "") -> None:

    file_name = f"{directory}/{audio_file.stem}.srt"
    print(f"Processing file {audio_file.name}\n\nFiles will be sent to {directory}\n\n")

    try:
        print(f"Transcribing {audio_file.name}...")
        segments, info = MODEL.transcribe(str(audio_file), language=language)
        duration = info.duration
        print(f"Audio duration: {duration:.1f}s | Language: {info.language} (prob: {info.language_probability:.2f})")
    except (OSError, RuntimeError, ValueError) as e:
        print(f"\nError processing {audio_file.name}: {e}\n Wrong file format?")
        return

    # Collect all segments
    try:
        srt_lines = []
        for idx, segment in enumerate(segments):
            start = format_timestamp(segment.start)
            end = format_timestamp(segment.end)
            text = segment.text.strip().replace("\n", " ")
            srt_lines.append(f"{idx+1}\n{start} --> {end}\n{text}\n")

            progress = min(segment.end / duration * 100, 100) if duration else 0
            print(f"  [{progress:5.1f}%] {start} → {end}  {text[:60]}")

        with open(file_name, "w", encoding="utf-8") as f:
            f.write("\n".join(srt_lines))

        print(f"\n✓ Generated {len(srt_lines)} subtitle segments → {file_name}")
    except OSError as e:
        print(f"\nError writing to file {file_name}: {e}")
        return

    subtitles_name, path = get_subtitle_file_path_name(file_name)
    style_subtitles(file=file_name, subtitle_name=subtitles_name, path=path)
