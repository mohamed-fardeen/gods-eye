# Testing Guide: Live Video Simulation & Trajectory Tracking

With the recent architectural shift, all AI components (YOLO, ByteTrack, PaddleOCR) have been fully moved to the `ai-worker`, keeping the backend ultra-lightweight. The frontend now features a live multi-camera video simulation dashboard to test cross-camera tracking and trajectory reconstruction.

Follow these steps to run a full end-to-end test on your local machine.

---

## 1. Environment Setup

Because the dependencies have shifted, you must update both environments.

### Backend Setup
1. Open a terminal and navigate to the `backend/` directory.
2. Activate your backend virtual environment.
3. Install the stripped-down dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *(This will ensure the heavy `torch`, `ultralytics`, and `paddleocr` packages are no longer loaded by the backend).*
4. Start the backend:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### AI Worker Setup
1. **Critical:** Place the fine-tuned model weights in their respective directories before starting:
   - YOLOv8 Plate Detector: Place `best.pt` inside `ai-worker/models/plate_detector/weights/`
   - PaddleOCR: Place `best_accuracy.pdparams` inside `ai-worker/models/ocr_ppocrv6_small/`
   *(These are currently untracked to keep the repo clean. Ask your teammate to provide them).*
2. Open a **new** terminal and navigate to the `ai-worker/` directory.
3. Activate your ai-worker virtual environment.
4. Install the updated dependencies (now including `httpx` and `rapidfuzz`):
   ```bash
   pip install -r requirements.txt
   ```
5. Start the AI Worker:
   ```bash
   uvicorn app.main:app --reload --port 8001
   ```

---

## 2. Running the Simulation

Once both servers are running successfully, you can use the frontend to upload and simulate video feeds.

### Start the Frontend
1. Open a **new** terminal and navigate to the `frontend/` directory.
2. Run the vanilla JS frontend (e.g., using a live server or python):
   ```bash
   python -m http.server 3000
   ```
3. Open your browser and go to `http://localhost:3000` (or whatever port you use).

### Upload Videos
1. In the sidebar, click on **Pipeline Test** (This has been repurposed into the Live Simulation Dashboard).
2. You will see a panel to upload multiple videos. 
3. For **Camera Source 1**:
   - Upload your first video file (`.mp4`, etc.).
   - Enter the **Latitude** and **Longitude** of where this camera is physically located.
   - Enter the **Start Time** (e.g., `2026-09-08 10:00 AM`).
4. For **Camera Source 2** (and subsequent cameras):
   - Upload your second video file.
   - Enter the **Latitude** and **Longitude**.
   - Enter the **Start Time** (e.g., `2026-09-08 10:05 AM`). 
   - *Note: Entering an accurate start time gap is crucial. The trajectory engine uses the time gap between camera detections to calculate real-world speed. If the vehicles travel impossibly fast between the two locations, the graph logic will reject the connection.*

### Execute the Test
1. Click **Start Simulation**.
2. The frontend will upload the videos to the backend's `temp/` folder and command the `ai-worker` to spin up parallel background processing threads for each video.
3. **Important:** As soon as you click start, navigate immediately to the **Digital Twin / Dashboard** or **Plate Search** maps.
4. Watch as the map live-updates. You will see vehicles detected by Camera 1, and as they appear in Camera 2's video, the backend will resolve their identity and draw the physical trajectory line on the map connecting the two nodes via OpenStreetMap data.
