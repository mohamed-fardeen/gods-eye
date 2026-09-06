"""
backend/app/services/pipeline_manager.py
=========================================
Singleton manager for live ANPRPipeline instances.

One pipeline per camera session. The API starts/stops pipelines;
the WebSocket broadcaster is wired as the on_alert / on_detection callback.

FastAPI startup wires everything:
    pipeline_manager.set_db_factory(get_db)
    pipeline_manager.set_broadcast_hook(ws_manager.broadcast)
"""
from __future__ import annotations

import asyncio
import logging
import threading
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


class PipelineManager:
    """
    Manages a pool of ANPRPipeline instances, keyed by camera_id.
    Thread-safe: pipelines run in daemon threads; this manager is accessed
    from FastAPI request threads.
    """

    def __init__(self) -> None:
        self._pipelines: Dict[str, Any] = {}  # camera_id → ANPRPipeline
        self._lock = threading.Lock()
        self._db_factory: Optional[Callable] = None
        self._broadcast_hook: Optional[Callable] = None
        self._event_loop: Optional[asyncio.AbstractEventLoop] = None

    def set_db_factory(self, factory: Callable) -> None:
        """Set the SQLAlchemy session factory (get_db generator)."""
        self._db_factory = factory

    def set_broadcast_hook(self, hook: Callable) -> None:
        """Set async broadcast coroutine; will be called with event dicts."""
        self._broadcast_hook = hook

    def set_event_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Store the running event loop so sync callbacks can schedule coroutines."""
        self._event_loop = loop

    def start_pipeline(
        self,
        camera_id: str,
        source: Any,
        watchlist_entries: Optional[list] = None,
    ) -> bool:
        """
        Start an ANPRPipeline for `camera_id` consuming `source`.
        Returns False if a pipeline for this camera_id is already running.
        """
        from app.ai.anpr_pipeline import ANPRPipeline, Watchlist, AlertEvent, DetectionEvent

        with self._lock:
            if camera_id in self._pipelines:
                existing = self._pipelines[camera_id]
                if existing.is_running:
                    logger.warning("Pipeline already running for %s", camera_id)
                    return False
                # Stale entry — clean it up
                del self._pipelines[camera_id]

        wl = Watchlist()
        if watchlist_entries:
            for entry in watchlist_entries:
                wl.add(entry["plate_text"], entry.get("reason", "flagged"))

        pipeline = ANPRPipeline(camera_id=camera_id, watchlist=wl)

        # Wire DB-persisting detection callback
        def _on_detection(evt: DetectionEvent) -> None:
            self._handle_detection(evt)

        def _on_alert(evt: AlertEvent) -> None:
            self._handle_alert(evt)

        pipeline.on_detection = _on_detection
        pipeline.on_alert = _on_alert

        with self._lock:
            self._pipelines[camera_id] = pipeline

        pipeline.start(source=source)
        logger.info("Pipeline started: camera=%s source=%s", camera_id, source)
        return True

    def stop_pipeline(self, camera_id: str) -> bool:
        with self._lock:
            pipeline = self._pipelines.pop(camera_id, None)
        if pipeline:
            pipeline.stop()
            logger.info("Pipeline stopped: camera=%s", camera_id)
            return True
        return False

    def stop_all(self) -> None:
        with self._lock:
            items = list(self._pipelines.items())
            self._pipelines.clear()
        for cam_id, pipeline in items:
            try:
                pipeline.stop()
            except Exception as exc:
                logger.error("Error stopping pipeline %s: %s", cam_id, exc)

    def list_running(self) -> Dict[str, bool]:
        with self._lock:
            return {
                cam_id: p.is_running
                for cam_id, p in self._pipelines.items()
            }

    def _handle_detection(self, evt: Any) -> None:
        """Persist detection to DB and broadcast via WebSocket."""
        if self._db_factory is None:
            return
        try:
            db_gen = self._db_factory()
            db = next(db_gen)
            try:
                from app.services.observation_service import ingest_detection
                ingest_detection(
                    db,
                    camera_id=evt.camera_id,
                    track_id=evt.track_id,
                    plate_text=evt.plate,
                    plate_det_confidence=None,      # already compounded in pipeline
                    ocr_confidence=None,
                    combined_confidence=evt.plate_confidence,
                    bbox=evt.vehicle_bbox,
                    frame_idx=evt.frame_idx,
                )
            finally:
                try:
                    next(db_gen)
                except StopIteration:
                    pass
        except Exception as exc:
            logger.error("DB ingest error (detection): %s", exc)

    def _handle_alert(self, evt: Any) -> None:
        """Broadcast alert and also broadcast it via WebSocket (high-priority)."""
        event_dict = evt.to_dict()
        self._async_broadcast(event_dict)
        logger.warning("Alert broadcast: %s", event_dict)

    def _async_broadcast(self, event_dict: Dict) -> None:
        """Schedule the async broadcast hook from a sync thread."""
        if self._broadcast_hook and self._event_loop:
            asyncio.run_coroutine_threadsafe(
                self._broadcast_hook(event_dict),
                self._event_loop,
            )


# Singleton
pipeline_manager = PipelineManager()
