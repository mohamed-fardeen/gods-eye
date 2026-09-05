from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from app.models.base import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, index=True) # e.g. VEHICLE_DETECTED, INCIDENT_DETECTED
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    location = Column(Geometry(geometry_type='POINT', srid=4326))
    source = Column(String)
    metadata_json = Column(JSON)
    status = Column(String, default="NEW")
