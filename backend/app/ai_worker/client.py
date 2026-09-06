import httpx
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.models.system_settings import SystemSettings

class AIWorkerClient:
    def __init__(self, db: Session):
        self.db = db
        self.mode = self._get_setting("AI_WORKER_MODE", "LOCAL")
        self.url = self._get_setting("AI_WORKER_URL", "http://localhost:8001")
        
    def _get_setting(self, key: str, default: str) -> str:
        setting = self.db.query(SystemSettings).filter(SystemSettings.key == key).first()
        if setting and setting.value:
            return setting.value
        return default

    async def get_health(self):
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get(f"{self.url}/health")
                response.raise_for_status()
                data = response.json()
                return {
                    "connected": True,
                    "mode": self.mode,
                    "url": self.url,
                    "device": data.get("device", "unknown"),
                    "gpu": data.get("gpu", None),
                    "models_loaded": data.get("models_loaded", False)
                }
        except Exception as e:
            return {
                "connected": False,
                "mode": self.mode,
                "url": self.url,
                "device": "unknown",
                "gpu": None,
                "models_loaded": False,
                "error": str(e)
            }

    async def infer(self, file: UploadFile):
        file_bytes = await file.read()
        await file.seek(0)
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                files = {'file': (file.filename, file_bytes, file.content_type)}
                response = await client.post(f"{self.url}/v1/inference", files=files)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            raise Exception(f"AI Worker inference failed: {str(e)}")
