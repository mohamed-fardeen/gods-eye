from sqlalchemy.orm import Session
from app.models.camera import Camera

class CameraRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        raise NotImplementedError("Database access is reserved for Phase 2.")
