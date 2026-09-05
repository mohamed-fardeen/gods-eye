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


@router.websocket("/events")
async def websocket_events(websocket: WebSocket):
    await websocket.accept()
    try:
        await websocket.send_json({
            "status": "not_implemented",
            "phase": "2",
            "message": "Real-time streaming over WebSocket is reserved for Phase 2."
        })
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo (Phase 1): {data}")
    except WebSocketDisconnect:
        pass
