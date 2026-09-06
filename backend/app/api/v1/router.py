from fastapi import APIRouter
from app.api.v1 import (
    system,
    vehicles,
    cameras,
    city,
    infrastructure,
    traffic,
    incidents,
    analytics,
    ws,
    observations,
    watchlist,
    pipeline,
    ocrtest,
    settings_api,
)

api_router = APIRouter()

# ── System ──────────────────────────────────────────────────────────────────
api_router.include_router(system.router,         prefix="/system",       tags=["System"])
api_router.include_router(settings_api.router,   prefix="/settings",     tags=["Settings"])
api_router.include_router(ocrtest.router,        prefix="/ocrtest",      tags=["OCR Testing"])

# ── ANPR Core (Phase 2) ─────────────────────────────────────────────────────
api_router.include_router(observations.router,   prefix="/observations", tags=["Observations"])
api_router.include_router(watchlist.router,      prefix="/watchlist",    tags=["Watchlist"])
api_router.include_router(pipeline.router,       prefix="/pipeline",     tags=["Pipeline Control"])

# ── Vehicles & Trajectory (Phase 2) ─────────────────────────────────────────
api_router.include_router(vehicles.router,       prefix="/vehicles",     tags=["Vehicles"])

# ── Infrastructure (Phase 2) ─────────────────────────────────────────────────
api_router.include_router(cameras.router,        prefix="/cameras",      tags=["Cameras"])
api_router.include_router(city.router,           prefix="/city",         tags=["City"])
api_router.include_router(infrastructure.router, prefix="/infrastructure", tags=["Infrastructure"])

# ── Analytics & Traffic (Phase 2) ────────────────────────────────────────────
api_router.include_router(traffic.router,        prefix="/traffic",      tags=["Traffic"])
api_router.include_router(incidents.router,      prefix="/incidents",    tags=["Incidents"])
api_router.include_router(analytics.router,      prefix="/analytics",    tags=["Analytics"])

# ── Real-time WebSocket ───────────────────────────────────────────────────────
api_router.include_router(ws.router,             prefix="/ws",           tags=["Real-time"])
