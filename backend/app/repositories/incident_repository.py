from sqlalchemy.orm import Session
from app.models.incident import Incident

class IncidentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_active(self):
        raise NotImplementedError("Database access is reserved for Phase 2.")
