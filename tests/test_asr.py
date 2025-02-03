# tests/test_asr.py

import tempfile
import os
from app.asr import load_model, transcribe_audio
from pydub import AudioSegment

def test_transcribe_audio():
    # Create a 1-second silent audio file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_audio:
        silent_audio = AudioSegment.silent(duration=1000)
        silent_audio.export(tmp_audio.name, format="wav")
        tmp_audio_path = tmp_audio.name

    try:
        model = load_model("tiny")
        result = transcribe_audio(model, tmp_audio_path)
        # The result should be a dict with a 'segments' key (even if empty)
        assert isinstance(result, dict)
        assert "segments" in result
    finally:
        if os.path.exists(tmp_audio_path):
            os.remove(tmp_audio_path)
