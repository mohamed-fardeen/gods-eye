"""
backend/app/services/observation_service.py
============================================
Handles ingestion and querying of ANPR pipeline observation events.

Flow:
  ANPRPipeline callback
    → POST /api/v1/observations  (HTTP) or ws event
      → observation_service.ingest()
        → identity_resolution_service.resolve_vehicle()
        → save Observation to DB
        → check watchlist → maybe create Incident + emit WS alert
        → broadcast live event over WebSocket
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.observation import Observation
from app.models.vehicle import Vehicle
from app.models.watchlist import WatchlistEntry
from app.models.incident import Incident
from app.services.identity_resolution_service import resolve_vehicle

logger = logging.getLogger(__name__)

# Module-level broadcast hook — set by the WebSocket manager at startup
# so the service layer doesn't import FastAPI directly.
_broadcast_hook: Optional[Callable[[Dict[str, Any]], None]] = None


def set_broadcast_hook(hook: Callable[[Dict[str, Any]], None]) -> None:
    """Register a callback that gets called with every live event dict."""
    global _broadcast_hook
    _broadcast_hook = hook


def _emit(event: Dict[str, Any]) -> None:
    if _broadcast_hook:
        try:
            _broadcast_hook(event)
        except Exception as exc:
            logger.warning("Broadcast hook error: %s", exc)


# ─────────────────────────────────────────────────────────────────────────────

def ingest_detection(
    db: Session,
    *,
    camera_id: str,
    track_id: int,
    plate_text: Optional[str],
    plate_det_confidence: Optional[float],
    ocr_confidence: Optional[float],
    combined_confidence: Optional[float],
    bbox: Optional[tuple] = None,           # (x1, y1, x2, y2)
    frame_idx: Optional[int] = None,
    observed_at: Optional[datetime] = None,
    metadata: Optional[Dict] = None,
) -> Observation:
    """
    Ingest one ANPR pipeline detection event:
      1. Resolve to a canonical Vehicle (identity resolution).
      2. Persist Observation row.
      3. Check watchlist → if hit, create Incident + set is_alert=True.
      4. Broadcast live update over WebSocket.
    """
    if observed_at is None:
        observed_at = datetime.now(timezone.utc)

    # ── 1. Identity resolution ────────────────────────────────────────────────
    vehicle: Optional[Vehicle] = None
    resolved_confidence = combined_confidence or 0.0
    if plate_text and plate_text != "UNKNOWN":
        vehicle, resolved_confidence = resolve_vehicle(
            db,
            plate_text=plate_text,
            combined_confidence=combined_confidence or 0.0,
        )

    # ── 2. Persist Observation ────────────────────────────────────────────────
    x1, y1, x2, y2 = bbox if bbox else (None, None, None, None)
    obs = Observation(
        camera_id=camera_id,
        track_id=track_id,
        plate_text=plate_text,
        plate_det_confidence=plate_det_confidence,
        ocr_confidence=ocr_confidence,
        combined_confidence=combined_confidence,
        bbox_x1=x1, bbox_y1=y1, bbox_x2=x2, bbox_y2=y2,
        vehicle_id=vehicle.id if vehicle else None,
        frame_idx=frame_idx,
        observed_at=observed_at,
        metadata_json=metadata,
    )
    db.add(obs)
    db.flush()  # get obs.id before the watchlist check

    # ── 3. Watchlist check ────────────────────────────────────────────────────
    alert_payload: Optional[Dict] = None
    if plate_text and plate_text != "UNKNOWN":
        wl_entry = (
            db.query(WatchlistEntry)
            .filter(WatchlistEntry.plate_text == plate_text, WatchlistEntry.is_active == True)
            .first()
        )
        if wl_entry is None:
            # Try fuzzy match against active watchlist entries
            from rapidfuzz import fuzz
            active_entries = db.query(WatchlistEntry).filter(
                WatchlistEntry.is_active == True
            ).all()
            for entry in active_entries:
                score = fuzz.ratio(plate_text.upper(), entry.plate_text.upper())
                if score >= 85:
                    wl_entry = entry
                    break

        if wl_entry:
            obs.is_alert = True
            wl_entry.alert_count += 1
            wl_entry.last_alerted_at = observed_at

            incident = Incident(
                title=f"Watchlist Alert: {plate_text}",
                description=(
                    f"Vehicle with plate {plate_text} matched watchlist entry "
                    f"'{wl_entry.plate_text}' (reason: {wl_entry.reason}). "
                    f"Seen at camera {camera_id}."
                ),
                severity="HIGH",
                reported_at=observed_at,
                status="ACTIVE",
            )
            db.add(incident)

            alert_payload = {
                "event_type": "WATCHLIST_ALERT",
                "camera_id": camera_id,
                "plate": plate_text,
                "matched_plate": wl_entry.plate_text,
                "reason": wl_entry.reason,
                "combined_confidence": round(resolved_confidence, 4),
                "observed_at": observed_at.isoformat(),
                "track_id": track_id,
            }
            logger.warning(
                "WATCHLIST ALERT: cam=%s plate=%s conf=%.3f",
                camera_id, plate_text, resolved_confidence,
            )

    db.commit()
    db.refresh(obs)

    # ── 4. Broadcast live update ───────────────────────────────────────────────
    detection_payload = {
        "event_type": "VEHICLE_DETECTED",
        "observation_id": obs.id,
        "camera_id": camera_id,
        "track_id": track_id,
        "plate": plate_text,
        "combined_confidence": round(combined_confidence or 0.0, 4),
        "vehicle_id": vehicle.id if vehicle else None,
        "observed_at": observed_at.isoformat(),
        "bbox": [x1, y1, x2, y2] if all(v is not None for v in [x1, y1, x2, y2]) else None,
    }
    _emit(detection_payload)
    if alert_payload:
        _emit(alert_payload)

    return obs


def get_trajectory(
    db: Session,
    plate_text: str,
    limit: int = 100,
) -> List[Dict]:
    """
    Return all observations for a vehicle identified by plate_text,
    ordered by observed_at ascending — this IS the trajectory.
    """
    from app.services.identity_resolution_service import _normalize_plate, _fuzzy_match_score, FUZZY_MATCH_THRESHOLD

    norm = _normalize_plate(plate_text)

    # Find the vehicle
    vehicle = db.query(Vehicle).filter(Vehicle.license_plate == norm).first()
    if not vehicle:
        # Fuzzy search
        all_vehicles = db.query(Vehicle).filter(Vehicle.license_plate.isnot(None)).all()
        best, best_score = None, 0.0
        for v in all_vehicles:
            s = _fuzzy_match_score(norm, v.license_plate)
            if s > best_score:
                best_score, best = s, v
        if best_score >= FUZZY_MATCH_THRESHOLD:
            vehicle = best
        else:
            return []

    observations = (
        db.query(Observation)
        .filter(Observation.vehicle_id == vehicle.id)
        .order_by(Observation.observed_at.asc())
        .limit(limit)
        .all()
    )

    return [
        {
            "observation_id": o.id,
            "camera_id": o.camera_id,
            "track_id": o.track_id,
            "plate_text": o.plate_text,
            "combined_confidence": o.combined_confidence,
            "bbox": [o.bbox_x1, o.bbox_y1, o.bbox_x2, o.bbox_y2],
            "observed_at": o.observed_at.isoformat() if o.observed_at else None,
            "frame_idx": o.frame_idx,
        }
        for o in observations
    ]


def get_recent_observations(
    db: Session,
    camera_id: Optional[str] = None,
    limit: int = 50,
) -> List[Dict]:
    """Return the most recent observations, optionally filtered by camera."""
    q = db.query(Observation).order_by(Observation.observed_at.desc())
    if camera_id:
        q = q.filter(Observation.camera_id == camera_id)
    observations = q.limit(limit).all()
    return [
        {
            "observation_id": o.id,
            "camera_id": o.camera_id,
            "track_id": o.track_id,
            "plate_text": o.plate_text,
            "combined_confidence": o.combined_confidence,
            "is_alert": o.is_alert,
            "observed_at": o.observed_at.isoformat() if o.observed_at else None,
        }
        for o in observations
    ]
