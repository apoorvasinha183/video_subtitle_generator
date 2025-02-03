# flask_app.py

import os
import tempfile
import threading
import uuid
from flask import Flask, render_template, request, jsonify, send_file
from app.main import process_video  # reuse your processing pipeline

app = Flask(__name__)

# Global dictionary to store job progress (job_id -> progress percentage)
job_progress = {}

@app.route('/', methods=['GET'])
def index():
    # Render a form with additional options (see next section for the template)
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    # Get the file from the form
    if 'video' not in request.files:
        return "No video file part", 400

    video_file = request.files['video']
    if video_file.filename == '':
        return "No selected file", 400

    # Retrieve extra options from the form (model size, target language, etc.)
    model_size = request.form.get('model_size', 'tiny')
    target_lang = request.form.get('target_lang')  # may be empty

    # Save the uploaded file to a temporary file
    temp_video = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
    video_file.save(temp_video)
    temp_video.close()

    output_srt = temp_video.name + ".srt"

    # Generate a unique job ID and initialize progress to 0%
    job_id = str(uuid.uuid4())
    job_progress[job_id] = 0

    # Define a progress callback function to update progress
    def progress_callback(current_chunk, total_chunks):
        percentage = int((current_chunk / total_chunks) * 100)
        job_progress[job_id] = percentage

    # Run the processing in a background thread
    def run_process():
        try:
            process_video(temp_video.name, output_srt, model_size, target_lang, progress_callback)
        except Exception as e:
            print("Error processing video:", e)
            job_progress[job_id] = -1  # indicate error

    thread = threading.Thread(target=run_process)
    thread.start()

    # Return the job_id to the client so that they can poll for progress
    return jsonify({"job_id": job_id})

@app.route('/progress', methods=['GET'])
def progress():
    job_id = request.args.get('job_id')
    if not job_id or job_id not in job_progress:
        return jsonify({"error": "Invalid job id"}), 400
    return jsonify({"progress": job_progress[job_id]})

@app.route('/download', methods=['GET'])
def download():
    # When processing is done (progress 100%), let the user download the file.
    job_id = request.args.get('job_id')
    output_srt = request.args.get('output')
    if not job_id or job_id not in job_progress:
        return "Invalid job id", 400
    # Here you can also add a check that job_progress[job_id]==100
    return send_file(output_srt, as_attachment=True, download_name="subtitles.srt")

if __name__ == '__main__':
    app.run(debug=True, port=5000)
