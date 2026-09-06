from sqlalchemy import Column, String, Text
from app.models.base import Base

class SystemSettings(Base):
    __tablename__ = "system_settings"

    key = Column(String, primary_key=True, index=True)
    value = Column(Text, nullable=True)
