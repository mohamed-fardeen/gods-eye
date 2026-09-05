from fastapi import APIRouter
from app.schemas.base import NotImplementedResponse

router = APIRouter()

@router.get("", response_model=NotImplementedResponse)
def get_analytics():
    return NotImplementedResponse()
