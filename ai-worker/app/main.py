from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
import time
import io
import cv2
import numpy as np
from contextlib import asynccontextmanager

from app.pipeline import TrafficVisionPipeline

# Global pipeline instance
pipeline: TrafficVisionPipeline = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global pipeline
    print("Loading models into AI worker memory...")
    pipeline = TrafficVisionPipeline()
    pipeline.load_models()
    print("Models loaded successfully.")
    yield
    print("Shutting down AI worker...")
    try:
        from app.pipeline_manager import pipeline_manager
        pipeline_manager.stop_all()
    except Exception as e:
        print(f"Error stopping pipelines: {e}")
    pipeline = None

app = FastAPI(title="AI Worker - Traffic Vision", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HealthResponse(BaseModel):
    status: str
    device: str
    gpu: str | None
    models_loaded: bool

@app.get("/health", response_model=HealthResponse)
def health_check():
    has_cuda = torch.cuda.is_available()
    device = "cuda" if has_cuda else "cpu"
    gpu = torch.cuda.get_device_name(0) if has_cuda else None
    loaded = pipeline is not None and pipeline.loaded
    
    return HealthResponse(
        status="ok",
        device=device,
        gpu=gpu,
        models_loaded=loaded
    )

@app.post("/v1/inference")
async def run_inference(file: UploadFile = File(...)):
    if not pipeline or not pipeline.loaded:
        raise HTTPException(status_code=503, detail="Models are not loaded yet.")
    
    # Basic image processing for now
    content = await file.read()
    
    # Decode image
    nparr = np.frombuffer(content, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if frame is None:
        raise HTTPException(status_code=400, detail="Invalid image format.")
    
    results = pipeline.process_image(frame)
    
    return results

class PipelineStartRequest(BaseModel):
    camera_id: str
    source: str
    watchlist_entries: list = []
    start_timestamp: float | None = None

@app.post("/v1/pipelines/start")
def start_pipeline(req: PipelineStartRequest):
    from app.pipeline_manager import pipeline_manager
    success = pipeline_manager.start_pipeline(
        req.camera_id, 
        req.source, 
        req.watchlist_entries,
        start_timestamp=req.start_timestamp
    )
    if not success:
        raise HTTPException(status_code=400, detail="Pipeline already running or could not start")
    return {"status": "started", "camera_id": req.camera_id}

@app.post("/v1/pipelines/stop/{camera_id}")
def stop_pipeline(camera_id: str):
    from app.pipeline_manager import pipeline_manager
    success = pipeline_manager.stop_pipeline(camera_id)
    if not success:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return {"status": "stopped", "camera_id": camera_id}
