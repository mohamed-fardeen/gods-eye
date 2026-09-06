# God's Eye — Project Status & Agent Memory
> **Living document. Update this file at every meaningful milestone and after every commit.**
> Last updated: 2026-09-06 16:33 IST | Branch: `tracking_ocr`

---

## 1. Project Identity

| Field | Value |
|---|---|
| **Competition** | Smart India Hackathon (SIH) 2026 |
| **Problem ID** | SIH26127 |
| **Sponsor** | Bharat Electronics Limited (BEL) |
| **Track** | Software — Transportation & Logistics / Smart Automation |
| **Project Name** | God's Eye — City-Wide AI Engine for Multi-Camera ANPR, Trajectory Tracking & Urban Traffic Analytics |

---

## 2. Problem Statement

Build a city-wide AI system that:
1. Performs **ANPR** with >90% accuracy
2. Reconstructs a single vehicle's **trajectory** across geographically distributed, non-overlapping cameras
3. Generates **city-wide traffic analytics** from aggregated vehicle movement
4. Raises **real-time alerts** for blacklisted/suspicious vehicles

---

## 3. Tech Stack

| Layer | Component | Tool |
|---|---|---|
| Vehicle detection | Object detector | YOLOv8/v11 (COCO pretrained) |
| Plate detection | Fine-tuned detector | YOLOv8n (HF: `Koushim/yolov8-license-plate-detection`) |
| Plate OCR | Text recognition | PaddleOCR PP-OCRv6 |
| Single-camera tracking | Multi-object tracker | ByteTrack/BoT-SORT (Ultralytics built-in) |
| Cross-camera Re-ID | Visual embedding | FastReID (secondary signal only) |
| Fuzzy plate matching | String similarity | Levenshtein + RapidFuzz |
| Road network | GIS | OpenStreetMap via Overpass API |
| Spatial DB | Database | PostgreSQL + PostGIS (SQLite for local dev) |
| Live state | In-memory store | Redis (not yet integrated) |
| Real-time push | Transport | WebSockets (native FastAPI) |
| Backend API | Framework | FastAPI (Python) |
| Frontend | Web app | Vite + Vanilla JS + CesiumJS + MapLibre GL JS |
| Graph reasoning | Simulation | NetworkX |
| Containers | Deployment | Docker Compose |

---

## 4. Repository Structure

```
gods-eye/
├── STATUS.md                           ← YOU ARE HERE (agent memory)
├── SIH26127_Solution_Architecture.txt  ← Full problem + solution spec
├── deep-research-report.md             ← ANPR pipeline design research
├── Untitled1.ipynb                     ← ANPR prototype (Colab notebook, v2)
├── frontend/                           ← ✅ COMPLETE — Vite + Vanilla JS app
│   ├── src/
│   │   ├── pages/          ← 10 pages (Dashboard, Cameras, PlateSearch, etc.)
│   │   ├── services/       ← CameraStreamManager.js (WebRTC), overpass.js
│   │   ├── cesium/         ← CesiumJS viewer, terrain, camera
│   │   ├── layers/         ← LayerManager, BuildingsLayer, BaseLayer
│   │   ├── ui/             ← Sidebar, Topbar, HUD components
│   │   ├── config/         ← coordinates.js (Chennai GPS anchor)
│   │   └── router.js       ← Hash-based SPA router
│   └── ...
└── backend/                            ← 🏗️ IN PROGRESS — FastAPI
    ├── app/
    │   ├── main.py         ← ✅ FastAPI app, CORS, router mount
    │   ├── core/
    │   │   ├── config.py   ← ✅ Settings (SQLite URI, project name)
    │   │   └── database.py ← ✅ SQLAlchemy engine + get_db()
    │   ├── models/         ← ✅ ORM models (all defined)
    │   ├── schemas/        ← ✅ base.py (NotImplementedResponse)
    │   ├── api/v1/
    │   │   ├── router.py   ← ✅ All sub-routers registered
    │   │   ├── system.py   ← ✅ GET /system/health
    │   │   ├── cameras.py  ← ✅ POST /cameras/register, GET /cameras/sessions
    │   │   ├── ws.py       ← ✅ WebRTC signaling WS + /ws/events (stub)
    │   │   ├── vehicles.py ← 🔴 STUB
    │   │   ├── traffic.py  ← 🔴 STUB
    │   │   ├── incidents.py← 🔴 STUB
    │   │   ├── analytics.py← 🔴 STUB
    │   │   ├── city.py     ← 🔴 STUB
    │   │   └── infrastructure.py ← 🔴 STUB
    │   ├── services/       ← 🔴 ALL STUBS (raise NotImplementedError)
    │   ├── repositories/   ← 🔴 ALL STUBS (raise NotImplementedError)
    │   └── ai/             ← 🔴 Protocol interfaces only (no ML code)
    │       ├── anpr.py
    │       ├── ocr.py
    │       ├── vehicle_detection.py
    │       ├── vehicle_tracking.py
    │       └── ...
    ├── requirements.txt    ← ✅ Base deps (fastapi, sqlalchemy, etc.)
    └── alembic/            ← ✅ Migration config
```

---

## 5. ORM Models (all in `backend/app/models/`)

| Model | Table | Key Columns |
|---|---|---|
| `Camera` | `cameras` | id, name, location (GeoPoint), is_active, stream_url |
| `CameraSession` | `camera_sessions` | session_id (UUID PK), camera_id (FK), name, device_type, status, lat, lon, timestamps |
| `Vehicle` | `vehicles` | id, license_plate, vehicle_type, color, first_seen, last_seen |
| `Detection` | `detections` | id, camera_id, object_class, confidence, timestamp |
| `Event` | `events` | id, type, timestamp, location (GeoPoint), source, metadata_json, status |
| `Incident` | `incidents` | id, title, description, severity, location (GeoPoint), reported_at, status |
| `TrafficRecord` | `traffic` | (check `traffic.py`) |
| `Building` | `buildings` | id, osm_id, name, geometry (Polygon), height |
| `Road` | `roads` | id, osm_id, name, type, geometry (LineString) |
| `City` | `cities` | (check `city.py`) |

---

## 6. Frontend Pages (all in `frontend/src/pages/`)

| Route | File | Status | Data Source |
|---|---|---|---|
| `#/` | `Dashboard.js` | ✅ UI done | Hardcoded mock |
| `#/map` | `DigitalTwin.js` | ✅ UI done | CesiumJS OSM tiles |
| `#/cameras` | `Cameras.js` | ✅ UI done | `GET /cameras/sessions` (real) |
| `#/plate-search` | `PlateSearch.js` | ✅ UI done | Hardcoded mock |
| `#/vehicle-profile` | `VehicleProfile.js` | ✅ UI done | Hardcoded mock |
| `#/traffic` | `Traffic.js` | ✅ UI done | Hardcoded mock |
| `#/incidents` | `Incidents.js` | ✅ UI done | Hardcoded mock |
| `#/camera-management` | `CameraManagement.js` | ✅ UI done | Hardcoded mock |
| `#/mobile-camera` | `MobileCamera.js` | ✅ UI done | `POST /cameras/register` + WS signaling (real) |
| `#/settings` | `Settings.js` | ✅ UI done | Hardcoded mock |
| `#/reports` | inline in `router.js` | ✅ UI done | Hardcoded mock |

**WebRTC**: `CameraStreamManager.js` singleton manages `RTCPeerConnection` connections across page navigations. Signaling via `/api/v1/ws/signaling/{session_id}?role=viewer|broadcaster`. This works end-to-end.

---

## 7. API Endpoints

### ✅ Implemented
| Method | Path | Description |
|---|---|---|
| GET | `/` | Root health check |
| GET | `/api/v1/system/health` | Service health |
| POST | `/api/v1/cameras/register` | Register mobile camera session |
| GET | `/api/v1/cameras/sessions` | List live camera sessions |
| WS | `/api/v1/ws/signaling/{session_id}` | WebRTC signaling relay |

### 🔴 Stubbed (returns `{"status": "not_implemented", "phase": "2"}`)
| Method | Path |
|---|---|
| GET | `/api/v1/cameras`, `/api/v1/cameras/{id}`, `/api/v1/cameras/{id}/stream` |
| GET | `/api/v1/vehicles`, `/api/v1/vehicles/{id}`, `/api/v1/vehicles/{id}/trajectory` |
| GET | `/api/v1/traffic` |
| GET | `/api/v1/incidents` |
| GET | `/api/v1/analytics` |
| GET | `/api/v1/city`, `/api/v1/infrastructure` |
| WS | `/api/v1/ws/events` (echoes only) |

---

## 8. ANPR Pipeline (from notebook `Untitled1.ipynb`)

The notebook (`v2`) contains a fully working prototype. Key design decisions:

- **Threading not asyncio**: YOLO/PaddleOCR are blocking C++/CUDA calls — they release the GIL, so real threads provide genuine parallelism. Asyncio would block the event loop.
- **Vehicle model**: `yolov8n.pt` (COCO pretrained) — classes 2,3,5,7 (car, motorcycle, bus, truck)
- **Plate model**: `Koushim/yolov8-license-plate-detection` (HF) — fine-tuned YOLOv8
- **OCR**: PaddleOCR PP-OCRv6 with oneDNN disabled (`PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT=0`)
- **3-channel fix**: grayscale → CLAHE → bilateral filter → `cv2.COLOR_GRAY2BGR` before PaddleOCR
- **Track-level voting**: `TrackState` with `Counter` for plate votes, avg confidence, grammar bonus
- **Early exit**: Once `CONFIDENT_VOTE_COUNT=3` votes for top plate → stop OCRing that track
- **Backpressure**: `queue.Queue(maxsize=8)` — capture thread blocks when processing lags
- **Fuzzy matching**: RapidFuzz `fuzz.ratio()` against watchlist (threshold: 85)
- **Confidence compound**: `plate_det_conf × ocr_conf` = combined score
- **Indian plate regex**: `^[A-Z]{2}\d{1,2}[A-Z]{0,3}\d{3,4}$` (soft weight bonus, not hard filter)
- **Confusion map**: O→0, I→1, B→8, S→5, Z→2

---

## 9. Backend Build Priority

| # | Component | Status | Files |
|---|---|---|---|
| 1 | **ANPR pipeline module** | ✅ DONE | `app/ai/anpr_pipeline.py` |
| 2 | **Observation ingestion API** | ✅ DONE | `app/api/v1/observations.py`, `app/services/observation_service.py` |
| 3 | **Identity resolution service** | ✅ DONE | `app/services/identity_resolution_service.py` |
| 4 | **Vehicle trajectory API** | ✅ DONE | `app/api/v1/vehicles.py` (real impl) |
| 5 | **Watchlist + alert engine** | ✅ DONE | `app/api/v1/watchlist.py`, `app/models/watchlist.py` |
| 6 | **WebSocket live events broadcast** | ✅ DONE | `app/api/v1/ws.py` → `DashboardManager` |
| 7 | **Pipeline control API** | ✅ DONE | `app/api/v1/pipeline.py`, `app/services/pipeline_manager.py` |
| 8 | **Road transition graph** (NetworkX) | 🔴 TODO | future |
| 9 | **Gap inference** | 🔴 TODO | future |
| 10 | **Traffic analytics** | 🔴 TODO | future |
| 11 | **LLM query agent** | 🔴 TODO | future |
| 12 | **Scenario simulator** | 🔴 TODO | future |

---

## 11. New Files & Architecture Updates (Phase 2)

| File / Component | Purpose |
|---|---|
| `ai-worker/` | Standalone Dockerized worker added in `main` branch. Hosts a FastAPI server, `pipeline.py`, and `ocr_utils.py` for isolated OCR testing and heavy ML loads. |
| `backend/app/ai/export_model.py` | Auto-compiles PyTorch YOLO weights (`yolov8n.pt`) to ONNX FP16 (`yolov8n.onnx`) for massive CPU/GPU speedups using `onnxruntime`. |
| `backend/app/ai/anpr_pipeline.py` | Core ANPR engine. Optimizations: `ProcessPoolExecutor` bypasses Python GIL, `SKIP_FRAMES=3` with ByteTrack interpolation, dropping queues for zero-latency, and heuristic early-exits. |
| `backend/app/models/observation.py` | Observation ORM (one vehicle sighting per camera per timestamp) |
| `backend/app/models/watchlist.py` | WatchlistEntry ORM |
| `backend/app/models/system_settings.py` | Added in `main` branch to handle dynamic system settings |
| `backend/app/services/observation_service.py` | Ingestion glue: identity resolution → DB → WS broadcast |
| `backend/app/services/identity_resolution_service.py` | Exact + fuzzy plate matching → canonical Vehicle |
| `backend/app/services/pipeline_manager.py` | Singleton: manages live ANPRPipeline instances per camera |
| `backend/app/api/v1/observations.py` | REST: ingest & query detections |
| `backend/app/api/v1/watchlist.py` | REST: add/remove/list blacklisted plates |
| `backend/app/api/v1/pipeline.py` | REST: start/stop/status pipeline per camera |
| `backend/app/api/v1/vehicles.py` | REST: search vehicles, get trajectory by plate or ID |
| `backend/app/api/v1/ocrtest.py` & `settings_api.py` | New API routes from `main` branch for the `ai-worker` integration |

---

## 12. Known Issues & Design Decisions

1. **SQLite geometry columns**: All `geoalchemy2.Geometry` columns replaced with plain `Float` lat/lon for SQLite local dev. Production path: PostgreSQL + PostGIS via Docker — columns are annotated with comments marking the migration target.
2. **No fake data policy**: All stubbed endpoints return `not_implemented`. Frontend pages show hardcoded mock data in JS (not seeded from DB).
3. **PaddleOCR MKLDNN crash**: Must set `PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT=0` and `FLAGS_use_mkldnn=0` **before** importing paddleocr. This is a known oneDNN/MKLDNN conflict.
4. **Hardware Acceleration**: Pipeline defaults to `ProcessPoolExecutor` (avoids Python GIL) and `onnxruntime`. Without a dedicated GPU, high CPU utilization and dropped frames will occur. With CUDA (e.g. RTX 5050), it achieves true zero-latency real-time 30FPS processing.
5. **Confidence-native requirement**: Every pipeline stage MUST emit a probability. Combined score = product of stage confidences. This is the architectural differentiator per the SIH problem spec.
6. **WebRTC signaling**: Already working end-to-end. Mobile phone → `POST /cameras/register` → WebSocket signaling → dashboard viewer.

---

## 13. Commit Log

| Date | Branch | Commit | Description |
|---|---|---|---|
| 2026-09-06 | `main` | (initial) | Frontend complete, backend skeleton |
| 2026-09-06 | `main` | 402b89d | Added `ai-worker`, OCR testing routes, SystemSettings, and notebook backup |
| 2026-09-06 | `tracking_ocr` | | Real-time ANPR pipeline optimization (ProcessPool, Frame Dropping, ONNX export, OpenCV UI, SQLite fixes) |
| 2026-09-06 | `tracking_ocr` | b1ce883 | Merged `origin/main` and resolved router/init conflicts |

---

## 14. Environment Setup

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### AI-Worker (Docker)
```bash
cd ai-worker
docker build -t ai-worker .
docker run -p 8001:8001 ai-worker
```

### Frontend
```bash
cd frontend
npm install
# Create .env.local with VITE_CESIUM_ION_TOKEN and VITE_BACKEND_URL
npm run dev   # http://localhost:3000
```
