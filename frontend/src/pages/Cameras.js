export function renderCameras() {
  return `
    <div class="page-padding page-fade" style="display: flex; flex-direction: column; gap: 20px; flex: 1; overflow-y: auto;">
      
      <!-- Top Toolbar -->
      <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 12px 20px;">
        <div style="display: flex; gap: 16px; align-items: center;">
          <h2 style="font-size: 16px; font-weight: 600; color: #fff; margin: 0;">CAMERA INTELLIGENCE</h2>
        </div>
        <button id="refresh-cameras-btn" class="btn btn-ghost" style="padding: 8px 16px; font-size: 12px;">↻ Refresh</button>
      </div>

      <!-- Main Layout -->
      <div id="live-cameras-container" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; flex: 1; align-content: start;">
        <!-- Cameras will be injected here dynamically -->
      </div>
      
      <div id="no-cameras-message" style="display: none; padding: 40px; text-align: center; color: var(--text-muted); font-size: 14px;">
        NO ACTIVE CAMERAS
      </div>

    </div>
  `;
}

export function initCameras() {
  const container = document.getElementById('live-cameras-container');
  const noCamerasMsg = document.getElementById('no-cameras-message');
  const refreshBtn = document.getElementById('refresh-cameras-btn');

  // We'll keep track of active viewer connections to close them on navigation or refresh
  const activeConnections = [];

  const iceServers = {
    iceServers: [
      { urls: 'stun:stun.l.google.com:19302' }
    ]
  };

  async function fetchLiveCameras() {
    try {
      // Clear previous connections
      activeConnections.forEach(conn => {
        if (conn.pc) conn.pc.close();
        if (conn.ws) conn.ws.close();
      });
      activeConnections.length = 0;
      container.innerHTML = '';

      const backendUrl = (import.meta.env.VITE_BACKEND_URL || '').replace(/\/$/, '');
      const response = await fetch(`${backendUrl}/api/v1/cameras/sessions`);
      if (!response.ok) throw new Error('Failed to fetch camera sessions');
      const sessions = await response.json();

      if (sessions.length === 0) {
        noCamerasMsg.style.display = 'block';
        return;
      }

      noCamerasMsg.style.display = 'none';

      sessions.forEach(session => {
        const camDiv = document.createElement('div');
        const shortId = `CAM-${session.session_id.substring(0, 4).toUpperCase()}`;
        camDiv.innerHTML = `
          <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; overflow: hidden; display: flex; flex-direction: column;">
            <div style="padding: 10px 14px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.05); background: rgba(0,0,0,0.2);">
              <div style="display: flex; flex-direction: column;">
                <span style="font-size:12px; font-weight:700; color:#fff;">${shortId}</span>
                <span style="font-size:11px; color:var(--text-muted);">${session.name}</span>
              </div>
              <div style="display:flex; align-items:center; gap:6px;">
                <div class="status-indicator live"></div>
                <span style="font-size:10px; font-weight:700; color:var(--success-color); text-transform:uppercase;">Live</span>
              </div>
            </div>
            <div style="aspect-ratio: 16/9; background: rgba(0,0,0,0.8); position: relative;">
              <video id="video-${session.session_id}" autoplay muted playsinline style="width: 100%; height: 100%; object-fit: cover;"></video>
            </div>
          </div>
        `;
        container.appendChild(camDiv);

        connectToSession(session.session_id);
      });
    } catch (err) {
      console.error(err);
      noCamerasMsg.style.display = 'block';
      noCamerasMsg.innerText = 'Error connecting to backend.';
    }
  }

  function connectToSession(sessionId) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const baseUrl = (import.meta.env.VITE_WS_URL || `${protocol}//${window.location.host}`).replace(/\/$/, '');
    const wsUrl = `${baseUrl}/api/v1/ws/signaling/${sessionId}?role=viewer`;
    const ws = new WebSocket(wsUrl);
    const pc = new RTCPeerConnection(iceServers);
    const videoEl = document.getElementById(`video-${sessionId}`);

    activeConnections.push({ ws, pc });

    pc.ontrack = (event) => {
      if (videoEl && event.streams && event.streams[0]) {
        videoEl.srcObject = event.streams[0];
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
        if (videoEl) videoEl.srcObject = null;
        pc.close();
        ws.close();
        // Remove from UI or refresh
        setTimeout(fetchLiveCameras, 1000);
      }
    };

    ws.onopen = () => {
      // In our design, the broadcaster sends an offer right away, but to trigger a new viewer,
      // we tell the broadcaster that we connected
      ws.send(JSON.stringify({ type: 'viewer_connected' }));
    };
  }

  refreshBtn.addEventListener('click', fetchLiveCameras);
  
  // Initial fetch
  fetchLiveCameras();
}
