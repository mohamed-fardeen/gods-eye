"""
backend/app/api/v1/watchlist.py
================================
Watchlist (blacklist) management API.
Operators add/remove plates here; the ANPR pipeline checks this list in
real-time and fires alerts (via WebSocket) when a match is found.
"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.watchlist import WatchlistEntry
from app.ai.anpr_pipeline import Watchlist as InMemoryWatchlist

router = APIRouter()

# In-memory watchlist kept in sync with the DB — the pipeline uses this directly.
# Populated at startup from DB by load_watchlist_from_db() called in main.py.
live_watchlist = InMemoryWatchlist()


def load_watchlist_from_db(db: Session) -> None:
    """Call at startup to seed the in-memory watchlist from the DB."""
    entries = db.query(WatchlistEntry).filter(WatchlistEntry.is_active == True).all()
    for entry in entries:
        live_watchlist.add(entry.plate_text, entry.reason or "flagged")


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class WatchlistAddRequest(BaseModel):
    plate_text: str
    reason: Optional[str] = "flagged"
    added_by: Optional[str] = None


class WatchlistEntryOut(BaseModel):
    id: int
    plate_text: str
    reason: Optional[str]
    is_active: bool
    added_by: Optional[str]
    added_at: Optional[datetime]
    alert_count: int
    last_alerted_at: Optional[datetime]


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("", response_model=List[WatchlistEntryOut])
def list_watchlist(db: Session = Depends(get_db)):
    """List all active watchlist entries."""
    entries = db.query(WatchlistEntry).filter(
        WatchlistEntry.is_active == True
    ).order_by(WatchlistEntry.added_at.desc()).all()
    return entries


@router.post("", response_model=WatchlistEntryOut, status_code=201)
def add_to_watchlist(payload: WatchlistAddRequest, db: Session = Depends(get_db)):
    """
    Add a plate to the watchlist. Takes effect immediately in the live pipeline.
    """
    plate = payload.plate_text.upper().replace(" ", "")

    existing = db.query(WatchlistEntry).filter(
        WatchlistEntry.plate_text == plate
    ).first()
    if existing:
        if existing.is_active:
            raise HTTPException(
                status_code=409,
                detail=f"Plate {plate} is already on the watchlist"
            )
        # Reactivate
        existing.is_active = True
        existing.reason = payload.reason
        existing.added_by = payload.added_by
        db.commit()
        db.refresh(existing)
        live_watchlist.add(plate, payload.reason or "flagged")
        return existing

    entry = WatchlistEntry(
        plate_text=plate,
        reason=payload.reason,
        added_by=payload.added_by,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    # Sync to in-memory watchlist used by the pipeline
    live_watchlist.add(plate, payload.reason or "flagged")
    return entry


@router.delete("/{plate_text}", status_code=204)
def remove_from_watchlist(plate_text: str, db: Session = Depends(get_db)):
    """Remove a plate from the watchlist. Takes effect immediately in the pipeline."""
    plate = plate_text.upper().replace(" ", "")
    entry = db.query(WatchlistEntry).filter(
        WatchlistEntry.plate_text == plate, WatchlistEntry.is_active == True
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail=f"Plate {plate} not on active watchlist")
    entry.is_active = False
    db.commit()
    live_watchlist.remove(plate)
