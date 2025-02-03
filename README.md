```markdown
# Video Subtitle Generator

A simple, real‑time video automated subtitle generator that uses pre‑trained ASR (Whisper) and a Flask API backend. It also supports translation using MarianMT from HuggingFace and includes a React-based web interface for uploading videos, selecting options, and tracking progress.

---

## Features

- **Audio Extraction:** Uses FFmpeg to extract audio from video files.
- **Audio Chunking:** Splits audio into overlapping chunks for near real‑time processing.
- **ASR:** Uses OpenAI's Whisper (tiny model by default) for transcription.
- **Subtitle Generation:** Generates SRT subtitle files.
- **API Mode:** Provides a Flask API for video file uploads, progress tracking, and subtitle downloads.
- **Translation:** Supports translation from English to a target language supported by the MarianMT HuggingFace model.
- **Frontend Interface:** A React-based web interface for file uploads, extra option selection (model size, target language), and a dynamic progress bar.
- **Containerization:** Dockerfile provided for containerized deployment.
- **CI/CD:** GitHub Actions for automated testing and deployment.

---

## Requirements

- **Python 3.9+**
- **FFmpeg** installed on your system
- **Node.js and npm** (for the React frontend)
- See **`requirements.txt`** for Python dependencies
- See **`package.json`** for JavaScript dependencies

---

## Project Structure

```plaintext
video_subtitle_generator/
├── app/                   # Core processing pipeline (audio extraction, ASR, translation, SRT generation)
│   ├── audio_extractor.py
│   ├── asr.py
│   ├── subtitle_generator.py
│   ├── translator.py
│   └── main.py            # Main processing pipeline script
├── flask_app.py           # Flask API that handles file uploads, progress reporting, and subtitle downloads
├── templates/             # HTML templates for Flask app (if needed)
├── frontend/              # React (or Vite) frontend project for uploading videos and displaying progress
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   ├── styles/
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json       # JavaScript dependencies
│   └── public/            # Static assets
├── Dockerfile             # For containerizing the application
├── requirements.txt       # Python dependencies
├── .github/workflows/     # CI/CD setup for GitHub Actions
└── README.md              # This file
```

---

## Usage

### 🔹 Running the Backend (Flask API)

1. **Start the Flask API**  
   In your project root, run:

   ```bash
   python flask_app.py
   ```

   This will start the backend on port **5001** (adjust if needed).

2. **API Endpoints:**
   - **`/upload`**: Accepts a video file and additional options (e.g., model size, target language). Returns a unique job ID.
   - **`/progress`**: Accepts a job ID and returns the current processing progress.
   - **`/download`**: Allows downloading the generated SRT subtitle file once processing is complete.

---

### 🔹 Running the Frontend (React)

1. **Install Dependencies and Start the React App**  
   In the **`frontend`** directory:

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

   The React app will typically run on **[http://localhost:5173](http://localhost:5173)** and will communicate with the Flask API.

2. **Using the Interface**:
   - Use the file upload form to select a video.
   - Choose additional options such as model size and target language via dropdowns and radio buttons.
   - The progress bar will update as the backend processes the video.
   - Once processing is complete, download the generated subtitle file.

---

### 🔹 Command-Line Processing (Optional)

If you prefer running the processing pipeline directly (without the web interface), you can use:

```bash
python -m app.main --video path/to/video.mp4 --output subtitles.srt
```

---

### 🔹 Docker Deployment

A **Dockerfile** is provided for containerized deployment. To build and run the Docker image:

```bash
docker build -t video_subtitle_generator .
docker run -p 5001:5001 video_subtitle_generator
```

---

## License

This project is licensed under the **MIT License**.
```