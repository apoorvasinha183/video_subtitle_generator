# app/main.py

import os
import shutil
import tempfile
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse
import uvicorn
import warnings
from tqdm import tqdm


from app.audio_extractor import extract_audio, split_audio
from app.asr import load_model, transcribe_audio
from app.subtitle_generator import generate_srt

from app.config import TEMP_AUDIO_DIR

# ------------------------------
# Command Line Processing Mode
# ------------------------------

def process_video(input_video: str, output_srt: str, model_size: str = "tiny",target_lang: str = None, progress_callback=None) -> None:
    """
    Process the video file:
      1. Extract audio.
      2. Split audio into chunks.
      3. Transcribe each chunk.
      4. Adjust segment timestamps.
      5. Generate SRT subtitles.
      6. Generate SRT subtitles.
    
    If target_lang is provided (e.g., "fr"), the transcription text will be translated.
    """
    # Create a temporary directory to store intermediate files
    temp_dir = tempfile.mkdtemp()

    try:
        # Step 1: Extract the audio from the video file
        audio_file = os.path.join(temp_dir, "audio.wav")
        extract_audio(input_video, audio_file)
        print(f"[INFO] Audio extracted to {audio_file}")

        # Step 2: Split audio into overlapping chunks
        chunks = split_audio(audio_file)
        print(f"[INFO] Split audio into {len(chunks)} chunks")
        total_chunks = len(chunks)
        # Step 3: Load ASR model
        model = load_model(model_size)
        print(f"[INFO] Loaded Whisper model ({model_size})")

        # Step 4: Transcribe each chunk and adjust timestamps
        all_segments = []
        chunk_num_processed = 0
        for chunk_file, offset_ms in tqdm(chunks,desc="Processing audio chunks"):
            result = transcribe_audio(model, chunk_file)
            # Each result contains segments relative to the chunk start (in seconds)
            for seg in result.get("segments", []):
                adjusted_seg = {
                    "start": seg["start"] + offset_ms / 1000.0,
                    "end": seg["end"] + offset_ms / 1000.0,
                    "text": seg["text"]
                }
                all_segments.append(adjusted_seg)
            #print(f"[INFO] Processed chunk at offset {offset_ms} ms")
            chunk_num_processed += 1
            if progress_callback :
                progress_callback(chunk_num_processed,total_chunks)
        # Optional Step 5: Translation
        if target_lang is not None:
            from app.translator import load_translation_model, translate_text
            # For now, we assume the source language is English ("en")
            tokenizer, translation_model = load_translation_model("en", target_lang)
            print(f"[INFO] Loaded translation model for en -> {target_lang}")
            for seg in all_segments:
                original_text = seg["text"]
                seg["text"] = translate_text(original_text, tokenizer, translation_model)
                print(f"[INFO] Translated: '{original_text}' -> '{seg['text']}'")
        # Optional: Sort segments by start time
        all_segments = sorted(all_segments, key=lambda x: x["start"])

        # Step 5: Generate the SRT file
        generate_srt(all_segments, output_srt)
        print(f"[INFO] Subtitle file generated at {output_srt}")
    finally:
        # Clean up temporary directory and files
        shutil.rmtree(temp_dir)
        # Optionally, remove the temp_audio folder created by split_audio:
        if os.path.exists(TEMP_AUDIO_DIR):
            shutil.rmtree(TEMP_AUDIO_DIR)

# ------------------------------
# API Mode using FastAPI
# ------------------------------

app = FastAPI(title="Video Subtitle Generator API")

@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    """
    Upload a video file, process it, and return the generated SRT file.
    """
    # Save the uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    output_srt = tmp_path + ".srt"

    try:
        process_video(tmp_path, output_srt)
        return FileResponse(output_srt, media_type="text/plain", filename="subtitles.srt")
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        # Clean up temporary files
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        if os.path.exists(output_srt):
            os.remove(output_srt)

# ------------------------------
# Main Entry Point
# ------------------------------

if __name__ == "__main__":
    import argparse
    warnings.filterwarnings("ignore", category=UserWarning)
    parser = argparse.ArgumentParser(description="Video Automated Subtitle Generator")
    parser.add_argument("--video", type=str, help="Path to the video file")
    parser.add_argument("--output", type=str, default="output.srt", help="Path for the output SRT file")
    parser.add_argument("--model", type=str, default="tiny", help="Whisper model size (e.g., tiny, small)")
    parser.add_argument("--target-lang", type=str, default=None, help="Target language code for translation (e.g., 'fr' for French)")
    parser.add_argument("--api", action="store_true", help="Run as an API server")
    args = parser.parse_args()

    if args.api:
        # Run the FastAPI server
        uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
    elif args.video:
        process_video(args.video, args.output, args.model)
    else:
        print("Please specify a video file to process or use --api to run the API server.")
