// Global Camera Stream Manager to persist WebRTC connections across page navigations

class CameraStreamManager {
  constructor() {
    this.activeConnections = new Map(); // sessionId -> { pc, ws, stream, status }
    this.iceServers = {
      iceServers: [
        { urls: 'stun:stun.l.google.com:19302' }
      ]
    };
    this.backendUrl = (import.meta.env.VITE_BACKEND_URL || '').replace(/\/$/, '');
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    this.wsBaseUrl = (import.meta.env.VITE_WS_URL || `${protocol}//${window.location.host}`).replace(/\/$/, '');
  }

  async getLiveSessions() {
    try {
      const response = await fetch(`${this.backendUrl}/api/v1/cameras/sessions`);
      if (!response.ok) return [];
      return await response.json();
    } catch (e) {
      console.error("Error fetching camera sessions:", e);
      return [];
    }
  }

  // Initiates or retrieves an existing connection, and attaches it to the videoElement
  connectToSession(sessionId, videoElement) {
    if (this.activeConnections.has(sessionId)) {
      const conn = this.activeConnections.get(sessionId);
      if (conn.stream && videoElement) {
        videoElement.srcObject = conn.stream;
      }
      return;
    }

    const wsUrl = `${this.wsBaseUrl}/api/v1/ws/signaling/${sessionId}?role=viewer`;
    const ws = new WebSocket(wsUrl);
    const pc = new RTCPeerConnection(this.iceServers);
    
    const connectionState = { pc, ws, stream: null, status: 'connecting' };
    this.activeConnections.set(sessionId, connectionState);

    pc.ontrack = (event) => {
      if (event.streams && event.streams[0]) {
        connectionState.stream = event.streams[0];
        connectionState.status = 'connected';
        if (videoElement) {
          videoElement.srcObject = event.streams[0];
        }
      }
    };

    pc.onicecandidate = (event) => {
      if (event.candidate && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
          type: 'candidate',
          candidate: event.candidate
        }));
      }
    };

    ws.onmessage = async (event) => {
      const msg = JSON.parse(event.data);

      if (msg.type === 'offer') {
        await pc.setRemoteDescription(new RTCSessionDescription(msg));
        const answer = await pc.createAnswer();
        await pc.setLocalDescription(answer);
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify(pc.localDescription));
        }
      } else if (msg.type === 'candidate') {
        await pc.addIceCandidate(new RTCIceCandidate(msg.candidate));
      } else if (msg.type === 'broadcaster_disconnected') {
        if (videoElement) videoElement.srcObject = null;
        this.disconnectSession(sessionId);
      }
    };
  }

  disconnectSession(sessionId) {
    const conn = this.activeConnections.get(sessionId);
    if (conn) {
      if (conn.pc) conn.pc.close();
      if (conn.ws) conn.ws.close();
      this.activeConnections.delete(sessionId);
    }
  }

  disconnectAll() {
    for (const sessionId of this.activeConnections.keys()) {
      this.disconnectSession(sessionId);
    }
  }
}

// Export a singleton instance
export const cameraStreamManager = new CameraStreamManager();
