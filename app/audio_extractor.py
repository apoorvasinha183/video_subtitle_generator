# app/audio_extractor.py

import os
import subprocess
from pydub import AudioSegment
from app.config import TEMP_AUDIO_DIR, CHUNK_LENGTH_MS, CHUNK_OVERLAP_MS

def extract_audio(input_video: str, output_audio: str) -> None:
    """
    Extract audio from the input video and save it as a WAV file.
    """
    command = [
        "ffmpeg",
        "-y",  # overwrite output file if it exists
        "-i", input_video,
        "-vn",  # no video
        "-acodec", "pcm_s16le",  # WAV format (PCM 16-bit little-endian)
        "-ar", "16000",  # sample rate (16 kHz, recommended for many ASR models)
        "-ac", "1",  # mono channel
        output_audio,
    ]
    subprocess.run(command, check=True)

def split_audio(audio_file: str) -> list:
    """
    Split the given audio file into overlapping chunks.

    Returns:
        A list of tuples: (chunk_file_path, start_time_ms)
    """
    if not os.path.exists(TEMP_AUDIO_DIR):
        os.makedirs(TEMP_AUDIO_DIR)

    audio = AudioSegment.from_file(audio_file)
    chunks = []
    start_ms = 0
    chunk_index = 0
    while start_ms < len(audio):
        end_ms = start_ms + CHUNK_LENGTH_MS
        chunk = audio[start_ms:end_ms]
        chunk_filename = os.path.join(TEMP_AUDIO_DIR, f"chunk_{chunk_index}.wav")
        chunk.export(chunk_filename, format="wav")
        chunks.append((chunk_filename, start_ms))
        # Advance by (chunk length - overlap)
        start_ms += (CHUNK_LENGTH_MS - CHUNK_OVERLAP_MS)
        chunk_index += 1

    return chunks
