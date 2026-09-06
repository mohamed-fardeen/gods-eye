from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.camera_session import CameraSession
from datetime import datetime
import json

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        # Maps session_id -> { "broadcaster": WebSocket, "viewers": [WebSocket] }
        self.active_sessions = {}

    async def connect_broadcaster(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = {"broadcaster": None, "viewers": []}
        self.active_sessions[session_id]["broadcaster"] = websocket

    async def connect_viewer(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = {"broadcaster": None, "viewers": []}
        self.active_sessions[session_id]["viewers"].append(websocket)

    def disconnect_broadcaster(self, session_id: str):
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["broadcaster"] = None

    def disconnect_viewer(self, session_id: str, websocket: WebSocket):
        if session_id in self.active_sessions:
            try:
                self.active_sessions[session_id]["viewers"].remove(websocket)
            except ValueError:
                pass

    async def broadcast_to_viewers(self, session_id: str, message: dict):
        if session_id in self.active_sessions:
            for viewer in self.active_sessions[session_id]["viewers"]:
                await viewer.send_json(message)

    async def send_to_broadcaster(self, session_id: str, message: dict):
        if session_id in self.active_sessions:
            broadcaster = self.active_sessions[session_id]["broadcaster"]
            if broadcaster:
                await broadcaster.send_json(message)

manager = ConnectionManager()

@router.websocket("/signaling/{session_id}")
async def signaling_endpoint(websocket: WebSocket, session_id: str, role: str = "viewer", db: Session = Depends(get_db)):
    """
    WebSocket endpoint for WebRTC signaling.
    role can be 'broadcaster' (the mobile phone) or 'viewer' (the dashboard).
    """
    
    # Verify session exists
    session_record = db.query(CameraSession).filter(CameraSession.session_id == session_id).first()
    if not session_record:
        await websocket.close(code=4004, reason="Session not found")
        return

    if role == "broadcaster":
        await manager.connect_broadcaster(session_id, websocket)
        session_record.status = "LIVE"
        session_record.connected_at = datetime.utcnow()
        db.commit()
    else:
        await manager.connect_viewer(session_id, websocket)
        await manager.send_to_broadcaster(session_id, {"type": "viewer_connected"})

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Simple signaling logic
            # Offer from broadcaster -> all viewers
            if message.get("type") == "offer" and role == "broadcaster":
                await manager.broadcast_to_viewers(session_id, message)
            
            # Answer from viewer -> broadcaster
            elif message.get("type") == "answer" and role == "viewer":
                await manager.send_to_broadcaster(session_id, message)
            
            # ICE candidates
            elif message.get("type") == "candidate":
                if role == "broadcaster":
                    await manager.broadcast_to_viewers(session_id, message)
                else:
                    await manager.send_to_broadcaster(session_id, message)

    except WebSocketDisconnect:
        if role == "broadcaster":
            manager.disconnect_broadcaster(session_id)
            session_record = db.query(CameraSession).filter(CameraSession.session_id == session_id).first()
            if session_record:
                session_record.status = "DISCONNECTED"
                session_record.disconnected_at = datetime.utcnow()
                db.commit()
            # Inform viewers that broadcaster disconnected
            await manager.broadcast_to_viewers(session_id, {"type": "broadcaster_disconnected"})
        else:
            manager.disconnect_viewer(session_id, websocket)



# ─────────────────────────────────────────────────────────────────────────────
# Dashboard Event Broadcaster
# ─────────────────────────────────────────────────────────────────────────────

class DashboardManager:
    """
    Manages all connected dashboard WebSocket clients.
    Events (vehicle detections, watchlist alerts, trajectory updates) are
    pushed here from the ANPRPipeline callbacks running in background threads.

    broadcast() is an async coroutine, called via asyncio.run_coroutine_threadsafe
    from the pipeline_manager when running outside the event loop.
    """

    def __init__(self) -> None:
        self._clients: list[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._clients.append(ws)

    def disconnect(self, ws: WebSocket) -> None:
        try:
            self._clients.remove(ws)
        except ValueError:
            pass

    async def broadcast(self, event: dict) -> None:
        """Send event to all connected dashboard clients."""
        dead = []
        for ws in list(self._clients):
            try:
                await ws.send_json(event)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

    @property
    def client_count(self) -> int:
        return len(self._clients)


dashboard_manager = DashboardManager()


@router.websocket("/events")
async def websocket_events(websocket: WebSocket):
    """
    Live event stream for the God's Eye dashboard.

    Clients connect here and receive a continuous stream of JSON events:
      - VEHICLE_DETECTED  — every ANPR detection with plate + confidence
      - WATCHLIST_ALERT   — high-priority, when a watchlist plate is spotted
      - SYSTEM            — heartbeat and status messages

    The pipeline_manager (running in background threads) calls
    dashboard_manager.broadcast() via asyncio.run_coroutine_threadsafe().
    """
    import asyncio

    await dashboard_manager.connect(websocket)
    try:
        # Send initial handshake
        await websocket.send_json({
            "event_type": "SYSTEM",
            "message": "Connected to God's Eye live event stream",
            "client_count": dashboard_manager.client_count,
        })

        # Keep connection alive; the server pushes events, client just listens.
        # A ping/pong every 30s prevents proxy timeout.
        while True:
            try:
                # Wait for any message (ping) from client or timeout
                await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
            except asyncio.TimeoutError:
                # Send heartbeat
                await websocket.send_json({"event_type": "HEARTBEAT"})
    except WebSocketDisconnect:
        pass
    finally:
        dashboard_manager.disconnect(websocket)
