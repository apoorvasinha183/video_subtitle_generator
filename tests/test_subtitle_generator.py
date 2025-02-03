# tests/test_subtitle_generator.py

import os
import tempfile
from app.subtitle_generator import generate_srt

def test_generate_srt():
    segments = [
        {"start": 0.0, "end": 1.5, "text": "Hello world."},
        {"start": 1.6, "end": 3.0, "text": "Testing subtitles."}
    ]
    with tempfile.NamedTemporaryFile(suffix=".srt", delete=False) as tmp_srt:
        srt_path = tmp_srt.name

    try:
        generate_srt(segments, srt_path)
        # Read the generated SRT file and check for expected content
        with open(srt_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert "Hello world." in content
            assert "Testing subtitles." in content
            assert "-->" in content
    finally:
        if os.path.exists(srt_path):
            os.remove(srt_path)
