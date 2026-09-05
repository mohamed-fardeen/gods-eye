from sqlalchemy import Column, Integer, String, Float
from geoalchemy2 import Geometry
from app.models.base import Base

class Building(Base):
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, index=True)
    osm_id = Column(String, index=True, nullable=True)
    name = Column(String, nullable=True)
    geometry = Column(Geometry(geometry_type='POLYGON', srid=4326))
    height = Column(Float, nullable=True)

class Road(Base):
    __tablename__ = "roads"

    id = Column(Integer, primary_key=True, index=True)
    osm_id = Column(String, index=True, nullable=True)
    name = Column(String, nullable=True)
    type = Column(String, nullable=True) # e.g. motorway, primary
    geometry = Column(Geometry(geometry_type='LINESTRING', srid=4326))
