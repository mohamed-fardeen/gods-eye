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
