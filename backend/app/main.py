"""
backend/app/main.py
====================
God's Eye — FastAPI application entry point.

Startup sequence:
  1. Create all DB tables (SQLAlchemy metadata.create_all).
  2. Load watchlist from DB into the in-memory pipeline watchlist.
  3. Wire the pipeline_manager with the DB factory, WebSocket broadcast hook,
     and the running asyncio event loop.
  4. Register all API routers.

Shutdown:
  - Stop all running ANPR pipelines gracefully.
"""

import asyncio
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, get_db, SessionLocal
from app.api.v1.router import api_router
import app.models  # noqa: F401 — import all models so metadata is populated

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "God's Eye — City-Wide AI Engine for Multi-Camera ANPR, "
        "Trajectory Tracking & Urban Traffic Analytics. SIH 2026 / BEL."
    ),
    version="0.2.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.on_event("startup")
async def startup_event():
    logger.info("Starting %s", settings.PROJECT_NAME)

    # ── 1. Create DB tables ───────────────────────────────────────────────────
    import app.models as _models
    _models.Base.metadata.create_all(bind=engine)
    logger.info("Database tables created / verified")

    # ── 2. Seed in-memory watchlist from DB ───────────────────────────────────
    try:
        from app.api.v1.watchlist import load_watchlist_from_db
        db = SessionLocal()
        try:
            load_watchlist_from_db(db)
            logger.info("Watchlist loaded from DB")
        finally:
            db.close()
    except Exception as exc:
        logger.warning("Could not load watchlist from DB: %s", exc)

    # ── 3. (Removed pipeline manager wiring, now handled by ai-worker) ────────

    # ── 4. Initialize Road Transition Graph ───────────────────────────────────
    try:
        from app.services.transition_graph import graph_service
        logger.info("Initializing Road Transition Graph (OSMNx)...")
        # Run in executor to not block the asyncio event loop startup for too long
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, graph_service.load_graph)
    except Exception as exc:
        logger.error("Failed to initialize Road Transition Graph: %s", exc)

    logger.info("%s ready. API docs: http://localhost:8000/docs", settings.PROJECT_NAME)


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down %s", settings.PROJECT_NAME)


@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": "0.2.0",
        "docs": "/docs",
        "status": "online",
        "branch": "tracking_ocr",
    }
