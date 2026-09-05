from sqlalchemy.orm import Session
from app.models.traffic import TrafficRecord

class TrafficRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_latest(self):
        raise NotImplementedError("Database access is reserved for Phase 2.")
