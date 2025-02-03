import { useState, useEffect } from "react";

function App() {
  const [videoFile, setVideoFile] = useState(null);
  const [modelSize, setModelSize] = useState("tiny");
  const [targetLang, setTargetLang] = useState("");
  const [progress, setProgress] = useState(0);
  const [jobId, setJobId] = useState(null);
  const [statusMessage, setStatusMessage] = useState("");

  const handleFileChange = (e) => {
    setVideoFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!videoFile) {
      alert("Please select a video file.");
      return;
    }

    const formData = new FormData();
    formData.append("video", videoFile);
    formData.append("model_size", modelSize);
    formData.append("target_lang", targetLang);

    try {
      const response = await fetch("http://localhost:5001/upload", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      if (data.job_id) {
        setJobId(data.job_id);
        setStatusMessage("Processing started...");
      } else {
        setStatusMessage("Upload failed.");
      }
    } catch (error) {
      console.error("Upload error:", error);
      setStatusMessage("Error uploading file.");
    }
  };

  useEffect(() => {
    let interval;
    if (jobId) {
      interval = setInterval(async () => {
        try {
          const response = await fetch(
            `http://localhost:5001/progress?job_id=${jobId}`
          );
          const data = await response.json();
          if (data.progress !== undefined) {
            setProgress(data.progress);
            if (data.progress >= 100) {
              setStatusMessage("Completed!");
              clearInterval(interval);
            }
          }
        } catch (error) {
          console.error("Progress error:", error);
        }
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [jobId]);

  return (
    <div className="App">
      <h1>Video Subtitle Generator</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label>
            Video File:
            <input
              type="file"
              accept="video/*"
              onChange={handleFileChange}
              required
            />
          </label>
        </div>
        <div>
          <label>
            Model Size:
            <select
              value={modelSize}
              onChange={(e) => setModelSize(e.target.value)}
            >
              <option value="tiny">Tiny</option>
              <option value="small">Small</option>
              <option value="medium">Medium</option>
            </select>
          </label>
        </div>
        <div>
          <label>Target Language:</label>
          <div>
            <input
              type="radio"
              id="none"
              name="target_lang"
              value=""
              checked={targetLang === ""}
              onChange={() => setTargetLang("")}
            />
            <label htmlFor="none">None</label>
          </div>
          <div>
            <input
              type="radio"
              id="hi"
              name="target_lang"
              value="hi"
              checked={targetLang === "hi"}
              onChange={() => setTargetLang("hi")}
            />
            <label htmlFor="hi">Hindi</label>
          </div>
          <div>
            <input
              type="radio"
              id="fr"
              name="target_lang"
              value="fr"
              checked={targetLang === "fr"}
              onChange={() => setTargetLang("fr")}
            />
            <label htmlFor="fr">French</label>
          </div>
        </div>
        <div>
          <button type="submit">Generate Subtitles</button>
        </div>
      </form>
      <div>
        <h2>Status: {statusMessage}</h2>
        <h3>Progress: {progress}%</h3>
        <div style={{ width: "100%", background: "#ddd", height: "30px" }}>
          <div
            style={{
              width: `${progress}%`,
              background: "#4CAF50",
              height: "100%",
              textAlign: "center",
              color: "white",
            }}
          >
            {progress}%
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
