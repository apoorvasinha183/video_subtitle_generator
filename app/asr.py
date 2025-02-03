# app/asr.py

import whisper

def load_model(model_size: str = "tiny") -> whisper.Whisper:
    """
    Load a Whisper ASR model. Options include 'tiny', 'small', etc.
    TODO: Allow the user to pick their own pre-trained ML model
    """
    model = whisper.load_model(model_size)
    return model

def transcribe_audio(model, audio_file: str) -> dict:
    """
    Transcribe the given audio file using the provided model.
    TODO: Specify the expected behavior of a custom model's output to match Whisper's output
    Returns:
        A dict containing the transcription and segments with start and end times.
    """
    # The transcribe method returns a dict with keys like 'text' and 'segments'
    result = model.transcribe(audio_file)
    return result
