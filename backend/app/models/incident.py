from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.sql import func
from app.models.base import Base

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String, nullable=True)
    severity = Column(String, default="LOW") # LOW, MEDIUM, HIGH, CRITICAL
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    reported_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="ACTIVE") # ACTIVE, RESOLVED

