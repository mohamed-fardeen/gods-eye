from fastapi import APIRouter
from app.schemas.base import NotImplementedResponse

router = APIRouter()

@router.get("", response_model=NotImplementedResponse)
def get_city_metadata():
    return NotImplementedResponse()

@router.get("/bounds", response_model=NotImplementedResponse)
def get_city_bounds():
    return NotImplementedResponse()
