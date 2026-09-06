"""
backend/app/models/observation.py
==================================
An 'Observation' is the core unit of the ANPR pipeline output:
one timestamped sighting of a vehicle at a specific camera,
with plate text and compound confidence score.

This is what the ANPR pipeline emits; the identity-resolution layer
then groups observations into per-vehicle trajectories.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.sql import func
from app.models.base import Base


class Observation(Base):
    """
    A single vehicle sighting at a single camera at a single point in time.

    Produced by: ANPRPipeline → observation_service → DB
    Consumed by: identity_resolution_service, trajectory_service, alert_engine

    Confidence fields:
      plate_det_confidence  — YOLO plate detection confidence [0,1]
      ocr_confidence        — PaddleOCR text recognition confidence [0,1]
      combined_confidence   — plate_det_confidence × ocr_confidence [0,1]
    """
    __tablename__ = "observations"

    id = Column(Integer, primary_key=True, index=True)

    # Camera that made this observation
    camera_id = Column(String, index=True, nullable=False)   # e.g. "CAM-01"

    # YOLO ByteTrack ID — unique per camera per run, NOT globally unique
    track_id = Column(Integer, nullable=False, index=True)

    # Plate recognition output
    plate_text = Column(String, nullable=True, index=True)
    plate_det_confidence = Column(Float, nullable=True)      # plate YOLO det conf
    ocr_confidence = Column(Float, nullable=True)            # PaddleOCR conf
    combined_confidence = Column(Float, nullable=True)       # product of above

    # Vehicle bounding box in the camera frame (pixels)
    bbox_x1 = Column(Integer, nullable=True)
    bbox_y1 = Column(Integer, nullable=True)
    bbox_x2 = Column(Integer, nullable=True)
    bbox_y2 = Column(Integer, nullable=True)

    # Link to resolved canonical vehicle (set by identity resolution)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True, index=True)

    # Whether this observation triggered a watchlist alert
    is_alert = Column(Boolean, default=False)

    # Frame number within the camera session (for ordering / debugging)
    frame_idx = Column(Integer, nullable=True)

    # When the observation happened
    observed_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Any extra metadata (e.g. raw OCR strings, alternative plate reads)
    metadata_json = Column(JSON, nullable=True)
