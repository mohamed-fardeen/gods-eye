from sqlalchemy import Column, Integer, String, Boolean
from geoalchemy2 import Geometry
from app.models.base import Base

class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    location = Column(Geometry(geometry_type='POINT', srid=4326))
    is_active = Column(Boolean, default=True)
    stream_url = Column(String, nullable=True)
