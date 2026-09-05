from sqlalchemy.orm import Session
from app.models.infrastructure import Building, Road

class InfrastructureRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_buildings(self):
        raise NotImplementedError("Database access is reserved for Phase 2.")

    def get_roads(self):
        raise NotImplementedError("Database access is reserved for Phase 2.")
