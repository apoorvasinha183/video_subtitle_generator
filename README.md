# Video Subtitle Generator

A simple, real‑time video automated subtitle generator using pre‑trained ASR (Whisper) and FastAPI.

## Features

- **Audio Extraction:** Uses FFmpeg to extract audio from video files.
- **Audio Chunking:** Splits audio into overlapping chunks for near real‑time processing.
- **ASR:** Uses OpenAI's Whisper (tiny model by default) for transcription.
- **Subtitle Generation:** Generates SRT subtitle files.
- **API Mode:** Provides a FastAPI endpoint for video file uploads.
- **Containerization:** Dockerfile provided for containerized deployment.

## Requirements

- Python 3.9+
- [FFmpeg](https://ffmpeg.org/) installed on your system
- See `requirements.txt` for Python dependencies

## Usage

### Command Line

```bash
python -m app.main --video path/to/video.mp4 --output subtitles.srt




