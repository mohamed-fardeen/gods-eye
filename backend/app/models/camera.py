from sqlalchemy import Column, Integer, String, Boolean, Float
from app.models.base import Base

class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    # Stored as plain lat/lon floats for SQLite compat.
    # In PostGIS deployment, migrate to Geometry(POINT, 4326).
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    heading = Column(Float, nullable=True)     # degrees 0-360, camera facing direction
    road_segment = Column(String, nullable=True)  # which road/lane this covers
    is_active = Column(Boolean, default=True)
    stream_url = Column(String, nullable=True)
    description = Column(String, nullable=True)
