# app/main.py

import os
import shutil
import tempfile
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse
import uvicorn

from app.audio_extractor import extract_audio, split_audio
from app.asr import load_model, transcribe_audio
from app.subtitle_generator import generate_srt

from app.config import TEMP_AUDIO_DIR

# ------------------------------
# Command Line Processing Mode
# ------------------------------

def process_video(input_video: str, output_srt: str, model_size: str = "tiny") -> None:
    """
    Process the video file:
      1. Extract audio.
      2. Split audio into chunks.
      3. Transcribe each chunk.
      4. Adjust segment timestamps.
      5. Generate SRT subtitles.
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

        # Step 3: Load ASR model
        model = load_model(model_size)
        print(f"[INFO] Loaded Whisper model ({model_size})")

        # Step 4: Transcribe each chunk and adjust timestamps
        all_segments = []
        for chunk_file, offset_ms in chunks:
            result = transcribe_audio(model, chunk_file)
            # Each result contains segments relative to the chunk start (in seconds)
            for seg in result.get("segments", []):
                adjusted_seg = {
                    "start": seg["start"] + offset_ms / 1000.0,
                    "end": seg["end"] + offset_ms / 1000.0,
                    "text": seg["text"]
                }
                all_segments.append(adjusted_seg)
            print(f"[INFO] Processed chunk at offset {offset_ms} ms")

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

    parser = argparse.ArgumentParser(description="Video Automated Subtitle Generator")
    parser.add_argument("--video", type=str, help="Path to the video file")
    parser.add_argument("--output", type=str, default="output.srt", help="Path for the output SRT file")
    parser.add_argument("--model", type=str, default="tiny", help="Whisper model size (e.g., tiny, small)")
    parser.add_argument("--api", action="store_true", help="Run as an API server")
    args = parser.parse_args()

    if args.api:
        # Run the FastAPI server
        uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
    elif args.video:
        process_video(args.video, args.output, args.model)
    else:
        print("Please specify a video file to process or use --api to run the API server.")
