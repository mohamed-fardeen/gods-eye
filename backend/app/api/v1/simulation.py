import os
import json
import uuid
from typing import List
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
import httpx

from app.core.database import get_db
from app.models.camera import Camera

router = APIRouter()

TEMP_DIR = os.path.join(os.getcwd(), "temp")
os.makedirs(TEMP_DIR, exist_ok=True)

AI_WORKER_URL = os.getenv("AI_WORKER_URL", "http://localhost:8001")

@router.post("/start_multi")
async def start_multi_simulation(
    videos: List[UploadFile] = File(...),
    metadata: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        meta_list = json.loads(metadata)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in metadata field")

    if len(videos) != len(meta_list):
        raise HTTPException(status_code=400, detail="Number of videos and metadata objects must match")

    results = []

    async with httpx.AsyncClient() as client:
        for i, video in enumerate(videos):
            meta = meta_list[i]
            
            camera_id = f"sim_cam_{uuid.uuid4().hex[:6]}"
            new_cam = Camera(
                id=camera_id,
                name=f"Simulated Camera {i+1}",
                latitude=meta.get("lat", 0.0),
                longitude=meta.get("lon", 0.0),
                status="online"
            )
            db.add(new_cam)
            
            ext = video.filename.split('.')[-1] if '.' in video.filename else "mp4"
            video_path = os.path.join(TEMP_DIR, f"{camera_id}.{ext}")
            
            content = await video.read()
            with open(video_path, "wb") as f:
                f.write(content)
                
            start_timestamp = None
            if "timestamp" in meta and meta["timestamp"]:
                try:
                    dt = datetime.fromisoformat(meta["timestamp"].replace('Z', '+00:00'))
                    start_timestamp = dt.timestamp()
                except Exception:
                    pass

            payload = {
                "camera_id": camera_id,
                "source": video_path,
                "start_timestamp": start_timestamp
            }
            
            try:
                resp = await client.post(f"{AI_WORKER_URL}/v1/pipelines/start", json=payload, timeout=10.0)
                resp.raise_for_status()
                results.append({"camera_id": camera_id, "status": "started", "video_path": video_path})
            except Exception as e:
                results.append({"camera_id": camera_id, "status": "failed", "error": str(e)})

        db.commit()

    return {"message": "Simulation started", "results": results}
