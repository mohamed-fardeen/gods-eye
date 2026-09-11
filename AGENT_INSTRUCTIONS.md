# Strict Instructions for AI Agents Contributing to this Repository

**ATTENTION AI AGENT:** If you are reading this file, you have been tasked with contributing to the "God's Eye" 3D Digital Twin & Traffic Intelligence repository. You **MUST** adhere strictly to the following architectural, branching, and integration rules. Failure to do so will break the project and force a revert.

## 1. Branching Strategy (DO NOT TOUCH MAIN)
- **You are FORBIDDEN from committing or merging directly to the `main` branch.**
- You must always work on your developer's specific feature branch (e.g., `feature/tracking`, `feature/analytics`).
- If your developer provides you with a standalone folder/script (e.g., a Jupyter notebook, a Python script testing OCR/Tracking), your job is to **integrate that logic into the existing architecture on their branch**, not to dump it into `main`.

## 2. Core Architectural Separation
This project is strictly divided into three distinct environments. **Do not mix them.**

### A. The Frontend (`frontend/`)
- Contains the React application and the CesiumJS 3D Map.
- **Rule:** Do not move WebRTC or camera signaling logic to the backend/AI worker. The phone (browser) acts as the camera and streams data to the backend.

### B. The Main Backend (`backend/`)
- A lightweight, high-performance FastAPI server.
- Handles WebRTC signaling, database connections (PostGIS), WebSocket streaming, and REST APIs.
- **CRITICAL RULE:** Do NOT install heavy machine learning libraries (`torch`, `ultralytics`, `paddleocr`, `opencv-python-headless`) in this container.
- **CRITICAL RULE:** Do NOT place inference logic, ML pipelines, or model weights (`.pt`, `.onnx`) in this folder. It must remain lightweight.

### C. The AI Worker (`ai-worker/`)
- A standalone microservice dedicated **exclusively** to heavy ML inference (YOLO, Tracking, Trajectory, OCR, ANPR).
- All new computer vision logic **MUST** be integrated here.
- Exposes a FastAPI interface (`/v1/inference`) that the Main Backend calls.
- Runs via Native Python using `run_local.bat` or `run_local.sh`. Do not force Docker on the AI worker unless explicitly requested, to preserve native GPU access on Windows.

## 3. How to Integrate New AI Code
When your developer gives you new AI code (e.g., a vehicle tracking or trajectory module), you must integrate it following these steps:

1. **Dependencies:** Add any new heavy ML dependencies (e.g., `deepsort`, `supervision`) to `ai-worker/requirements.txt`, **NOT** to `backend/requirements.txt`.
2. **Models:** Download and place model weights inside `ai-worker/models/`. **Ensure they are added to `.gitignore` so they are not committed to GitHub.**
3. **Execution:** Integrate the logic into `ai-worker/app/pipeline.py` or create a new module inside `ai-worker/app/`. 
4. **Efficiency:** Models MUST be loaded globally **ONCE** when the `ai-worker` starts. Do NOT load models on every frame or every API request.
5. **Communication:** The main `backend` will send image frames to the `ai-worker`. The `ai-worker` processes them and returns JSON results (bounding boxes, track IDs, OCR text). Do not try to make the `ai-worker` talk directly to the frontend or database.

## 4. Preservation of Existing Features
- **Do not rewrite existing infrastructure.** If you are asked to add tracking, add it to the existing inference pipeline without breaking the current WebRTC streaming or Cesium marker systems.
- Always check `backend/app/ai_worker/client.py` and `ai-worker/app/main.py` to understand the existing API contract before changing the JSON response schemas.

## Summary Checklist for AI Agents
- [ ] Am I on a feature branch (NOT main)?
- [ ] Did I put the heavy ML logic in `ai-worker/`?
- [ ] Is the main `backend/` free of PyTorch/Ultralytics?
- [ ] Are model weights excluded from git commits?
- [ ] Are models loaded globally once, not per frame?

**Acknowledge these rules in your thought process before executing any tool calls or writing code.**
