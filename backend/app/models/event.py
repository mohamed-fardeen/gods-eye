from sqlalchemy import Column, Integer, String, DateTime, JSON, Float
from sqlalchemy.sql import func
from app.models.base import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, index=True) # e.g. VEHICLE_DETECTED, INCIDENT_DETECTED
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    source = Column(String)
    metadata_json = Column(JSON)
    status = Column(String, default="NEW")

