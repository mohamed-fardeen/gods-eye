from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from app.models.base import Base

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String, nullable=True)
    severity = Column(String, default="LOW") # LOW, MEDIUM, HIGH, CRITICAL
    location = Column(Geometry(geometry_type='POINT', srid=4326))
    reported_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="ACTIVE") # ACTIVE, RESOLVED
