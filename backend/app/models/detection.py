from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.models.base import Base

class Detection(Base):
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, index=True) # Conceptual link to Camera
    object_class = Column(String) # e.g. Person, Car, Motorcycle
    confidence = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
