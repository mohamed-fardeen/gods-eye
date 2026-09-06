from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.models.system_settings import SystemSettings
from app.ai_worker.client import AIWorkerClient

router = APIRouter()

class AIWorkerSettingsUpdate(BaseModel):
    mode: str
    url: str

@router.get("/ai-worker")
async def get_ai_worker_settings(db: Session = Depends(get_db)):
    client = AIWorkerClient(db)
    health = await client.get_health()
    return health

@router.post("/ai-worker")
def update_ai_worker_settings(settings: AIWorkerSettingsUpdate, db: Session = Depends(get_db)):
    # Update MODE
    mode_setting = db.query(SystemSettings).filter(SystemSettings.key == "AI_WORKER_MODE").first()
    if not mode_setting:
        mode_setting = SystemSettings(key="AI_WORKER_MODE", value=settings.mode)
        db.add(mode_setting)
    else:
        mode_setting.value = settings.mode

    # Update URL
    url_setting = db.query(SystemSettings).filter(SystemSettings.key == "AI_WORKER_URL").first()
    if not url_setting:
        url_setting = SystemSettings(key="AI_WORKER_URL", value=settings.url)
        db.add(url_setting)
    else:
        url_setting.value = settings.url
        
    db.commit()
    return {"message": "Settings updated successfully"}
