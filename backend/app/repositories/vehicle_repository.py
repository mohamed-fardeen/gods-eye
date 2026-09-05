from sqlalchemy.orm import Session
from app.models.vehicle import Vehicle

class VehicleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_recent(self):
        raise NotImplementedError("Database access is reserved for Phase 2.")
