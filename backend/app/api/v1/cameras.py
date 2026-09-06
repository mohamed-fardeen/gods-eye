from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.camera_session import CameraSession
from app.schemas.base import NotImplementedResponse
from pydantic import BaseModel
import uuid
from datetime import datetime

router = APIRouter()

class RegisterCameraRequest(BaseModel):
    name: str
    latitude: float | None = None
    longitude: float | None = None

@router.post("/register")
def register_camera_session(req: RegisterCameraRequest, db: Session = Depends(get_db)):
    """
    Registers a new mobile camera session before establishing WebRTC.
    """
    session_id = str(uuid.uuid4())
    
    # We are not tying it to a permanent Camera record yet, just creating a Session.
    db_session = CameraSession(
        session_id=session_id,
        name=req.name,
        device_type="MOBILE_BROWSER",
        status="CONNECTING",
        latitude=req.latitude,
        longitude=req.longitude
    )
    
    db.add(db_session)
    db.commit()
    
    return {
        "status": "success",
        "session_id": session_id,
        "name": req.name
    }

@router.get("/sessions")
def get_live_sessions(db: Session = Depends(get_db)):
    """
    Returns all currently live sessions.
    """
    sessions = db.query(CameraSession).filter(CameraSession.status.in_(["CONNECTING", "LIVE"])).all()
    return [{
        "session_id": s.session_id,
        "name": s.name,
        "status": s.status,
        "connected_at": s.connected_at,
        "latitude": s.latitude,
        "longitude": s.longitude
    } for s in sessions]


@router.get("", response_model=NotImplementedResponse)
def get_cameras():
    return NotImplementedResponse()

@router.get("/{camera_id}", response_model=NotImplementedResponse)
def get_camera(camera_id: int):
    return NotImplementedResponse()

@router.get("/{camera_id}/stream", response_model=NotImplementedResponse)
def get_camera_stream(camera_id: int):
    return NotImplementedResponse()
