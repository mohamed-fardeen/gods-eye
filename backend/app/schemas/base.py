from pydantic import BaseModel

class NotImplementedResponse(BaseModel):
    status: str = "not_implemented"
    phase: str = "2"
    message: str = "This module is reserved for Phase 2."
