"""
backend/app/api/v1/pipeline.py
================================
Pipeline control API — start/stop ANPR processing on a camera source.

POST /api/v1/pipeline/start   — start pipeline for a camera
POST /api/v1/pipeline/stop    — stop pipeline for a camera
GET  /api/v1/pipeline/status  — list all running pipelines
"""
from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.pipeline_manager import pipeline_manager

router = APIRouter()


class PipelineStartRequest(BaseModel):
    camera_id: str
    source: Any                          # int (webcam), str (file/RTSP URL)
    watchlist_entries: Optional[list] = None   # [{plate_text, reason}]


@router.post("/start")
def start_pipeline(payload: PipelineStartRequest):
    """
    Start an ANPR pipeline for a camera.

    source examples:
      0                          → default webcam
      "rtsp://192.168.1.5/live"  → IP camera RTSP stream
      "/path/to/video.mp4"       → video file (for testing)
      "session:<session_id>"     → future: tap a WebRTC session frame stream
    """
    started = pipeline_manager.start_pipeline(
        camera_id=payload.camera_id,
        source=payload.source,
        watchlist_entries=payload.watchlist_entries,
    )
    if not started:
        raise HTTPException(
            status_code=409,
            detail=f"Pipeline for camera '{payload.camera_id}' is already running."
        )
    return {
        "status": "started",
        "camera_id": payload.camera_id,
        "source": str(payload.source),
    }


@router.post("/stop")
def stop_pipeline(camera_id: str):
    """Stop the ANPR pipeline for a camera."""
    stopped = pipeline_manager.stop_pipeline(camera_id)
    if not stopped:
        raise HTTPException(
            status_code=404,
            detail=f"No running pipeline found for camera '{camera_id}'."
        )
    return {"status": "stopped", "camera_id": camera_id}


@router.get("/status")
def pipeline_status():
    """List all currently running pipelines and their state."""
    return {
        "running_pipelines": pipeline_manager.list_running(),
        "count": len(pipeline_manager.list_running()),
    }
