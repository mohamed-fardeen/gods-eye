# God's Eye — Project Status

## Current Phase: Phase 2 & Architecture Decoupling (Completed)

We have successfully overhauled the architecture of the system to prepare for robust, GPU-accelerated container deployments and live simulation testing. The AI components have been entirely decoupled from the backend routing, resulting in a clean, microservice-like structure.

### 1. Architectural Overhaul
- **`ai-worker` Dedicated Service:** All heavy AI operations (YOLOv8 vehicle detection, ByteTrack multi-frame object tracking, and PaddleOCR license plate reading) have been moved completely to the `ai-worker`.
- **Backend Decoupling:** The `backend` is now purely a data management layer (API, PostgreSQL/SQLite, WebSocket broadcasting). It no longer requires bulky ML dependencies like `torch`, `ultralytics`, or `paddleocr`. 
- **HTTP Inter-Service Communication:** The `pipeline_manager` inside the `ai-worker` now asynchronously sends `HTTP POST` requests containing normalized vehicle track events to the backend (`/api/v1/observations`), rather than executing direct SQL transactions.

### 2. Multi-Camera Simulation Dashboard
- **Frontend Live Upload:** The `#/ocrtest` endpoint has been fully converted into a **Live Video Simulation Dashboard**.
- **Synchronized Timestamps:** Users can dynamically upload multiple concurrent video files representing different CCTV cameras. By assigning physical metadata (Latitude, Longitude) and logical metadata (Start Time), the system accurately simulates real-world delays.
- **Backend Orchestration:** The backend (`/api/v1/simulation/start_multi`) stores the uploaded video files locally, registers temporary camera entities in the database, and orchestrates the `ai-worker` to spin up parallel inference pipelines for each stream.
- **Live Graph Integration:** As the `ai-worker` processes the videos, detections flow into the backend where the **Identity Resolution Service** groups them into vehicles. The **Road Transition Graph** uses `osmnx` to draw and validate realistic geographic paths between the camera nodes, piping straight to the live web UI.

## Next Steps: Phase 3 (Traffic Analytics & Alerts)
With the AI decoupled and the trajectory engine tested via the Simulation Dashboard, the next phase focuses on aggregated intelligence:
1. **Speed & Congestion Metrics:** Aggregate vehicle trajectories to compute road link speeds and detect traffic jams based on OSM map links.
2. **Watchlist Alerting Pipelines:** Finalize the visual flagging in the frontend map whenever a watchlist plate is successfully matched across the streaming cameras.
3. **Data Expiration & Cleanup:** Implement TTL (Time To Live) mechanisms to prune stale tracks and observations so the system can run indefinitely.
