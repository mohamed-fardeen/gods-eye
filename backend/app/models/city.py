from sqlalchemy import Column, Integer, String, Float
from geoalchemy2 import Geometry
from app.models.base import Base

class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    country = Column(String)
    bounds = Column(Geometry(geometry_type='POLYGON', srid=4326))
