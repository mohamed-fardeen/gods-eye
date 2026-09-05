from sqlalchemy import Column, Integer, Float, DateTime
from sqlalchemy.sql import func
from app.models.base import Base

class TrafficRecord(Base):
    __tablename__ = "traffic_records"

    id = Column(Integer, primary_key=True, index=True)
    road_id = Column(Integer, index=True) # Conceptual link to Road
    volume = Column(Integer, default=0)
    average_speed = Column(Float, nullable=True)
    congestion_index = Column(Float, default=0.0) # 0.0 to 1.0
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
