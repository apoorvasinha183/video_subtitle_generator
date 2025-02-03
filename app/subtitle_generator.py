# app/subtitle_generator.py

import math

def format_timestamp(ms: float) -> str:
    """
    Convert milliseconds to SRT time format: HH:MM:SS,mmm
    """
    seconds, millis = divmod(ms, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{int(millis):03}"

def generate_srt(segments: list, output_file: str) -> None:
    """
    Generate an SRT file from the provided segments.

    Each segment in `segments` should be a dict with keys: 'start', 'end', 'text'.
    The 'start' and 'end' are in seconds.
    """
    with open(output_file, "w", encoding="utf-8") as f:
        for idx, seg in enumerate(segments, start=1):
            start_ms = seg["start"] * 1000
            end_ms = seg["end"] * 1000
            f.write(f"{idx}\n")
            f.write(f"{format_timestamp(start_ms)} --> {format_timestamp(end_ms)}\n")
            f.write(f"{seg['text'].strip()}\n\n")
