from fastapi import APIRouter
from app.schemas.base import NotImplementedResponse

router = APIRouter()

@router.get("", response_model=NotImplementedResponse)
def get_infrastructure():
    return NotImplementedResponse()

@router.get("/buildings", response_model=NotImplementedResponse)
def get_buildings():
    return NotImplementedResponse()

@router.get("/roads", response_model=NotImplementedResponse)
def get_roads():
    return NotImplementedResponse()
