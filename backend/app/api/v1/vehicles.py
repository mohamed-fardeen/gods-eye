"""
backend/app/api/v1/vehicles.py
================================
Vehicle search and trajectory endpoints.
These replace the previous stubs with real DB-backed implementations.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.vehicle import Vehicle
from app.services.observation_service import get_trajectory, get_recent_observations

router = APIRouter()


@router.get("")
def search_vehicles(
    plate: Optional[str] = Query(None, description="Plate text (partial or full)"),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    """
    Search vehicles by plate text. Supports partial (substring) matching.
    Returns list of vehicle records with their last-seen info.
    """
    q = db.query(Vehicle)
    if plate:
        q = q.filter(Vehicle.license_plate.ilike(f"%{plate.upper()}%"))
    vehicles = q.order_by(Vehicle.last_seen.desc()).limit(limit).all()
    return [
        {
            "vehicle_id": v.id,
            "license_plate": v.license_plate,
            "vehicle_type": v.vehicle_type,
            "color": v.color,
            "first_seen": v.first_seen.isoformat() if v.first_seen else None,
            "last_seen": v.last_seen.isoformat() if v.last_seen else None,
        }
        for v in vehicles
    ]


@router.get("/{vehicle_id}")
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    """Get a single vehicle by its internal ID."""
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return {
        "vehicle_id": v.id,
        "license_plate": v.license_plate,
        "vehicle_type": v.vehicle_type,
        "color": v.color,
        "first_seen": v.first_seen.isoformat() if v.first_seen else None,
        "last_seen": v.last_seen.isoformat() if v.last_seen else None,
    }


@router.get("/by-plate/{plate_text}/trajectory")
def get_vehicle_trajectory(
    plate_text: str,
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
):
    """
    Get the full trajectory (ordered camera sightings) for a vehicle identified
    by plate text. Supports fuzzy matching so minor OCR errors still resolve.

    Returns a list of observation dicts ordered by observed_at ascending —
    the trajectory is time-ordered camera hits with confidence scores.
    This is the core output that feeds the Vehicle Profile page on the dashboard.
    """
    trajectory = get_trajectory(db, plate_text=plate_text, limit=limit)
    if not trajectory:
        raise HTTPException(
            status_code=404,
            detail=f"No trajectory found for plate '{plate_text}'"
        )
    return {
        "plate_text": plate_text.upper(),
        "total_sightings": len(trajectory),
        "trajectory": trajectory,
    }


@router.get("/{vehicle_id}/trajectory")
def get_vehicle_trajectory_by_id(
    vehicle_id: int,
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
):
    """
    Get trajectory for a vehicle by its internal DB ID.
    """
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if not v.license_plate:
        return {"vehicle_id": vehicle_id, "total_sightings": 0, "trajectory": []}

    trajectory = get_trajectory(db, plate_text=v.license_plate, limit=limit)
    return {
        "vehicle_id": vehicle_id,
        "license_plate": v.license_plate,
        "total_sightings": len(trajectory),
        "trajectory": trajectory,
    }
