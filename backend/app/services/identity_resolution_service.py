"""
backend/app/services/identity_resolution_service.py
=====================================================
Resolves each ANPR observation to a canonical Vehicle DB record.

Resolution cascade (confidence-weighted, per architecture doc §3.1):
  1. Exact plate match  → highest confidence, return existing vehicle
  2. Fuzzy plate match  → edit-distance within threshold, return existing
                          vehicle (with slightly reduced confidence)
  3. No match           → create new Vehicle record

Confidence compound:
  resolved_confidence = observation.combined_confidence × match_confidence
  match_confidence is 1.0 for exact match, fuzzy_score/100 for fuzzy.

This module is called by the observation ingestion endpoint after each
ANPR pipeline event arrives.
"""
from __future__ import annotations

import logging
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.models.vehicle import Vehicle
from app.models.observation import Observation

logger = logging.getLogger(__name__)

# Levenshtein / fuzzy threshold for plate matching.
# Must be consistent with the value in anpr_pipeline.py (FUZZY_MATCH_THRESHOLD).
FUZZY_MATCH_THRESHOLD = 85


def _normalize_plate(plate: str) -> str:
    """Uppercase, strip spaces. No confusion-map here — raw normalized form."""
    return plate.upper().replace(" ", "").strip()


def _fuzzy_match_score(a: str, b: str) -> float:
    """
    Returns RapidFuzz ratio score [0, 100] between two normalized plate strings.
    Kept as a standalone function so it's testable without DB.
    """
    try:
        from rapidfuzz import fuzz
        return fuzz.ratio(a, b)
    except ImportError:
        # Fallback: simple Levenshtein
        return 100.0 if a == b else 0.0


def resolve_vehicle(
    db: Session,
    plate_text: str,
    combined_confidence: float,
    vehicle_type: Optional[str] = None,
) -> Tuple[Vehicle, float]:
    """
    Resolve a plate text to a canonical Vehicle record.

    Returns:
        (vehicle, resolved_confidence)
        resolved_confidence = combined_confidence × match_factor
          where match_factor = 1.0 for exact, fuzzy_score/100 for fuzzy.

    Side effects: may INSERT a new Vehicle row if no match found.
    """
    if not plate_text or plate_text == "UNKNOWN":
        return _create_vehicle(db, plate_text=None, vehicle_type=vehicle_type), 0.0

    norm_plate = _normalize_plate(plate_text)

    # ── 1. Exact match ────────────────────────────────────────────────────────
    existing = db.query(Vehicle).filter(
        Vehicle.license_plate == norm_plate
    ).first()
    if existing:
        logger.debug("Identity: exact match %s → Vehicle#%d", norm_plate, existing.id)
        return existing, combined_confidence * 1.0

    # ── 2. Fuzzy match ────────────────────────────────────────────────────────
    # Load all known plates and find best fuzzy match.
    # In a large deployment this should be cached in Redis or use a DB trigram
    # index (PostgreSQL pg_trgm). For the prototype scope this is fine.
    all_vehicles = db.query(Vehicle).filter(
        Vehicle.license_plate.isnot(None)
    ).all()

    best_vehicle: Optional[Vehicle] = None
    best_score = 0.0

    for vehicle in all_vehicles:
        if not vehicle.license_plate:
            continue
        score = _fuzzy_match_score(norm_plate, vehicle.license_plate)
        if score > best_score:
            best_score = score
            best_vehicle = vehicle

    if best_score >= FUZZY_MATCH_THRESHOLD and best_vehicle is not None:
        match_factor = best_score / 100.0
        resolved_confidence = combined_confidence * match_factor
        logger.info(
            "Identity: fuzzy match %s → Vehicle#%d (score=%.0f, resolved_conf=%.3f)",
            norm_plate, best_vehicle.id, best_score, resolved_confidence,
        )
        return best_vehicle, resolved_confidence

    # ── 3. New vehicle ────────────────────────────────────────────────────────
    new_vehicle = _create_vehicle(db, plate_text=norm_plate, vehicle_type=vehicle_type)
    logger.info("Identity: new vehicle created plate=%s id=%d", norm_plate, new_vehicle.id)
    return new_vehicle, combined_confidence


def _create_vehicle(
    db: Session,
    plate_text: Optional[str],
    vehicle_type: Optional[str],
) -> Vehicle:
    vehicle = Vehicle(
        license_plate=plate_text,
        vehicle_type=vehicle_type,
    )
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle
