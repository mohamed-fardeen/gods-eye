"""
backend/app/api/v1/observations.py
====================================
REST endpoints for ANPR pipeline observation ingestion and querying.

POST /api/v1/observations        — ingest one detection event from the pipeline
GET  /api/v1/observations        — list recent observations (with camera filter)
GET  /api/v1/observations/{id}   — single observation detail
"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.observation_service import (
    ingest_detection,
    get_recent_observations,
)
from app.models.observation import Observation

router = APIRouter()


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class ObservationIngest(BaseModel):
    """Payload sent by the ANPR pipeline (or a camera agent) per detection."""
    camera_id: str
    track_id: int
    plate_text: Optional[str] = None
    plate_det_confidence: Optional[float] = None
    ocr_confidence: Optional[float] = None
    combined_confidence: Optional[float] = None
    bbox: Optional[List[int]] = None          # [x1, y1, x2, y2]
    frame_idx: Optional[int] = None
    observed_at: Optional[datetime] = None
    metadata: Optional[dict] = None


class ObservationResponse(BaseModel):
    observation_id: int
    camera_id: str
    track_id: int
    plate_text: Optional[str]
    combined_confidence: Optional[float]
    is_alert: bool
    vehicle_id: Optional[int]
    observed_at: Optional[datetime]

    class Config:
        from_attributes = True


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("", response_model=ObservationResponse, status_code=201)
def ingest_observation(payload: ObservationIngest, db: Session = Depends(get_db)):
    """
    Ingest a single ANPR detection event.

    This endpoint is called by:
     - The local ANPR pipeline (via HTTP callback or direct call)
     - Edge camera agents that run detection locally and send only metadata

    Triggers: identity resolution, watchlist check, WebSocket broadcast.
    """
    bbox = tuple(payload.bbox) if payload.bbox and len(payload.bbox) == 4 else None
    obs = ingest_detection(
        db,
        camera_id=payload.camera_id,
        track_id=payload.track_id,
        plate_text=payload.plate_text,
        plate_det_confidence=payload.plate_det_confidence,
        ocr_confidence=payload.ocr_confidence,
        combined_confidence=payload.combined_confidence,
        bbox=bbox,
        frame_idx=payload.frame_idx,
        observed_at=payload.observed_at,
        metadata=payload.metadata,
    )
    return ObservationResponse(
        observation_id=obs.id,
        camera_id=obs.camera_id,
        track_id=obs.track_id,
        plate_text=obs.plate_text,
        combined_confidence=obs.combined_confidence,
        is_alert=obs.is_alert,
        vehicle_id=obs.vehicle_id,
        observed_at=obs.observed_at,
    )


@router.get("", response_model=List[dict])
def list_observations(
    camera_id: Optional[str] = Query(None),
    limit: int = Query(50, le=500),
    db: Session = Depends(get_db),
):
    """Return the most recent observations, optionally filtered by camera_id."""
    return get_recent_observations(db, camera_id=camera_id, limit=limit)


@router.get("/{observation_id}", response_model=dict)
def get_observation(observation_id: int, db: Session = Depends(get_db)):
    obs = db.query(Observation).filter(Observation.id == observation_id).first()
    if not obs:
        raise HTTPException(status_code=404, detail="Observation not found")
    return {
        "observation_id": obs.id,
        "camera_id": obs.camera_id,
        "track_id": obs.track_id,
        "plate_text": obs.plate_text,
        "plate_det_confidence": obs.plate_det_confidence,
        "ocr_confidence": obs.ocr_confidence,
        "combined_confidence": obs.combined_confidence,
        "bbox": [obs.bbox_x1, obs.bbox_y1, obs.bbox_x2, obs.bbox_y2],
        "vehicle_id": obs.vehicle_id,
        "is_alert": obs.is_alert,
        "frame_idx": obs.frame_idx,
        "observed_at": obs.observed_at.isoformat() if obs.observed_at else None,
        "metadata": obs.metadata_json,
    }
