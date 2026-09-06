from fastapi import APIRouter
from app.api.v1 import system, vehicles, cameras, city, infrastructure, traffic, incidents, analytics, ws, ocrtest, settings_api

api_router = APIRouter()

api_router.include_router(system.router, prefix="/system", tags=["System"])
api_router.include_router(city.router, prefix="/city", tags=["City (Phase 2)"])
api_router.include_router(infrastructure.router, prefix="/infrastructure", tags=["Infrastructure (Phase 2)"])
api_router.include_router(vehicles.router, prefix="/vehicles", tags=["Vehicles (Phase 2)"])
api_router.include_router(cameras.router, prefix="/cameras", tags=["Cameras (Phase 2)"])
api_router.include_router(traffic.router, prefix="/traffic", tags=["Traffic (Phase 2)"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["Incidents (Phase 2)"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics (Phase 2)"])
api_router.include_router(ws.router, prefix="/ws", tags=["Real-time (Phase 2)"])
api_router.include_router(ocrtest.router, prefix="/ocrtest", tags=["OCR Testing"])
api_router.include_router(settings_api.router, prefix="/settings", tags=["Settings"])
