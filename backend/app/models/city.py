from sqlalchemy import Column, Integer, String, Float
from app.models.base import Base

class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    country = Column(String)
    # Bounding box as plain floats (SQLite-compatible).
    # In PostGIS: replace with Geometry(POLYGON, 4326).
    bounds_min_lat = Column(Float, nullable=True)
    bounds_min_lon = Column(Float, nullable=True)
    bounds_max_lat = Column(Float, nullable=True)
    bounds_max_lon = Column(Float, nullable=True)

