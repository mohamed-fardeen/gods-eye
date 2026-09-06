"""
backend/app/models/watchlist.py
================================
Stores the operator-managed blacklist / watchlist of plates.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.models.base import Base


class WatchlistEntry(Base):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, index=True)
    plate_text = Column(String, nullable=False, index=True, unique=True)
    reason = Column(String, nullable=True)           # e.g. "stolen", "wanted"
    is_active = Column(Boolean, default=True)
    added_by = Column(String, nullable=True)         # operator role / user
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    last_alerted_at = Column(DateTime(timezone=True), nullable=True)
    alert_count = Column(Integer, default=0)
