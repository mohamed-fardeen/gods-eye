from sqlalchemy import Column, Integer, String, Float
from app.models.base import Base

class Building(Base):
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, index=True)
    osm_id = Column(String, index=True, nullable=True)
    name = Column(String, nullable=True)
    # GeoJSON/WKT string for SQLite; use PostGIS Geometry in production
    geometry_wkt = Column(String, nullable=True)
    height = Column(Float, nullable=True)

class Road(Base):
    __tablename__ = "roads"

    id = Column(Integer, primary_key=True, index=True)
    osm_id = Column(String, index=True, nullable=True)
    name = Column(String, nullable=True)
    type = Column(String, nullable=True) # e.g. motorway, primary
    # GeoJSON/WKT string for SQLite; use PostGIS Geometry in production
    geometry_wkt = Column(String, nullable=True)
    # For road transition graph: store camera-pair travel times
    min_travel_time_s = Column(Float, nullable=True)
    max_travel_time_s = Column(Float, nullable=True)

