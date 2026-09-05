from sqlalchemy.orm import Session
from app.models.city import City

class CityRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_city(self):
        raise NotImplementedError("Database access is reserved for Phase 2.")
