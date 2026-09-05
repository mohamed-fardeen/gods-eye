from fastapi import APIRouter
from app.schemas.base import NotImplementedResponse

router = APIRouter()

@router.get("", response_model=NotImplementedResponse)
def get_vehicles():
    return NotImplementedResponse()

@router.get("/{vehicle_id}", response_model=NotImplementedResponse)
def get_vehicle(vehicle_id: int):
    return NotImplementedResponse()

@router.get("/{vehicle_id}/trajectory", response_model=NotImplementedResponse)
def get_vehicle_trajectory(vehicle_id: int):
    return NotImplementedResponse()
