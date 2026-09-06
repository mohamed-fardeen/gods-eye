from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from app.models.base import Base

class CameraSession(Base):
    __tablename__ = "camera_sessions"

    session_id = Column(String, primary_key=True, index=True) # UUID string
    camera_id = Column(Integer, ForeignKey("cameras.id"), index=True, nullable=True) # Optional link to registered camera
    name = Column(String)
    device_type = Column(String, default="MOBILE_BROWSER")
    status = Column(String, default="CONNECTING") # CONNECTING, LIVE, DISCONNECTED, ERROR
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    connected_at = Column(DateTime(timezone=True), nullable=True)
    disconnected_at = Column(DateTime(timezone=True), nullable=True)
