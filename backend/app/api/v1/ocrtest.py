from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.ai_worker.client import AIWorkerClient

router = APIRouter()

@router.post("")
async def test_ocr_pipeline(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Proxies the uploaded image/video to the configured AI Worker for processing.
    """
    client = AIWorkerClient(db)
    
    # Check if worker is healthy
    health = await client.get_health()
    if not health["connected"]:
        raise HTTPException(
            status_code=503, 
            detail=f"AI Worker is unreachable. Mode: {health['mode']}, URL: {health['url']}, Error: {health.get('error')}"
        )
        
    if not health["models_loaded"]:
        raise HTTPException(
            status_code=503,
            detail="AI Worker is connected but models are not loaded yet."
        )

    # Perform inference
    try:
        results = await client.infer(file)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
