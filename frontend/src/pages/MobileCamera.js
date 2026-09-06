export function renderMobileCamera() {
  return `
    <div class="page-padding page-fade" style="max-width: 600px; margin: 0 auto; display: flex; flex-direction: column; gap: 20px;">
      
      <div style="text-align: center; margin-bottom: 10px;">
        <h2 style="font-size: 20px; font-weight: 600; letter-spacing: 1px;">ADD CAMERA</h2>
        <p style="color: var(--text-muted); font-size: 14px;">Mobile CCTV Broadcaster</p>
      </div>

      <div class="panel" id="camera-setup-panel">
        <div class="panel-body" style="display: flex; flex-direction: column; gap: 16px;">
          <div>
            <label style="display: block; font-size: 12px; font-weight: 600; margin-bottom: 6px;">CAMERA NAME</label>
            <input type="text" id="mobile-cam-name" class="search-input" value="Mobile Camera 01" style="width: 100%; box-sizing: border-box;" />
          </div>
          <div>
            <label style="display: block; font-size: 12px; font-weight: 600; margin-bottom: 6px;">LOCATION</label>
            <button id="btn-get-location" class="btn btn-ghost" style="width: 100%; justify-content: center; margin-bottom: 6px;">📍 Use Current Location</button>
            <div id="location-display" style="font-size: 12px; color: var(--text-muted); text-align: center;">Location not set</div>
          </div>
          
          <button id="btn-start-camera" class="btn btn-primary" style="width: 100%; justify-content: center; padding: 14px; font-size: 16px; font-weight: 600; margin-top: 10px;">
            START LIVE CAMERA
          </button>
        </div>
      </div>

      <div class="panel" id="camera-live-panel" style="display: none;">
        <div class="panel-body" style="display: flex; flex-direction: column; gap: 16px;">
          
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 8px;">
              <div class="status-indicator live"></div>
              <span id="live-status-text" style="font-weight: 600; font-size: 14px;">CONNECTING...</span>
            </div>
            <span id="session-id-display" style="font-size: 12px; color: var(--text-muted); font-family: monospace;"></span>
          </div>

          <div style="width: 100%; aspect-ratio: 16/9; background: #000; border-radius: 8px; overflow: hidden; position: relative;">
            <video id="mobile-video-preview" autoplay muted playsinline style="width: 100%; height: 100%; object-fit: cover;"></video>
          </div>

          <button id="btn-stop-camera" class="btn" style="background: var(--error-color); color: white; border: none; width: 100%; justify-content: center; padding: 14px; font-size: 16px; font-weight: 600;">
            STOP CAMERA
          </button>

        </div>
      </div>

    </div>
  `;
}

export function initMobileCamera() {
  const btnStart = document.getElementById('btn-start-camera');
  const btnStop = document.getElementById('btn-stop-camera');
  const btnLocation = document.getElementById('btn-get-location');
  const setupPanel = document.getElementById('camera-setup-panel');
  const livePanel = document.getElementById('camera-live-panel');
  const videoPreview = document.getElementById('mobile-video-preview');
  const statusText = document.getElementById('live-status-text');
  const sessionIdDisplay = document.getElementById('session-id-display');
  
  let localStream = null;
  let peerConnection = null;
  let signalingSocket = null;
  let currentSessionId = null;

  // ICE Servers config (STUN/TURN) - Currently public Google STUN for testing
  const iceServers = {
    iceServers: [
      { urls: 'stun:stun.l.google.com:19302' }
    ]
  };
  
  // Auto-fetch location on load
  let currentLat = null;
  let currentLng = null;
  let locationStatus = 'pending'; // pending, success, failed

  function fetchLocation() {
    if (navigator.geolocation) {
      document.getElementById('location-display').innerText = 'Fetching GPS...';
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          currentLat = pos.coords.latitude;
          currentLng = pos.coords.longitude;
          locationStatus = 'success';
          document.getElementById('location-display').innerText = `Lat: ${currentLat.toFixed(4)}, Lng: ${currentLng.toFixed(4)}`;
        },
        (err) => {
          locationStatus = 'failed';
          document.getElementById('location-display').innerText = 'GPS access denied/failed';
          console.warn('Geolocation error:', err);
        },
        { enableHighAccuracy: true, timeout: 10000 }
      );
    } else {
      locationStatus = 'failed';
      document.getElementById('location-display').innerText = 'GPS not supported';
    }
  }

  fetchLocation();

  btnLocation.addEventListener('click', () => {
    fetchLocation();
  });

  btnStart.addEventListener('click', async () => {
    const camName = document.getElementById('mobile-cam-name').value || 'Mobile Camera';
    
    if (locationStatus === 'pending') {
      alert("Please wait for GPS location to be fetched, or ensure location permissions are granted.");
      return;
    }
    
    try {
      // 1. Get Camera Permission & Stream
      localStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' }, audio: false });
      videoPreview.srcObject = localStream;
      
      setupPanel.style.display = 'none';
      livePanel.style.display = 'block';

      // 2. Register Session with Backend
      const backendUrl = (import.meta.env.VITE_BACKEND_URL || '').replace(/\/$/, '');
      // Use the fetched coordinates directly
      let lat = currentLat;
      let lng = currentLng;

      const response = await fetch(`${backendUrl}/api/v1/cameras/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: camName, latitude: lat, longitude: lng })
      });
      
      if (!response.ok) throw new Error('Failed to register camera session on backend.');
      
      const data = await response.json();
      currentSessionId = data.session_id;
      sessionIdDisplay.innerText = `CAM-${currentSessionId.substring(0, 4).toUpperCase()}`;

      // 3. Connect to Signaling Server
      connectSignaling(currentSessionId);

    } catch (err) {
      alert('Could not start camera: ' + err.message);
      console.error(err);
      stopCamera();
    }
  });

  btnStop.addEventListener('click', () => {
    stopCamera();
    setupPanel.style.display = 'block';
    livePanel.style.display = 'none';
  });

  function connectSignaling(sessionId) {
    // Determine WS protocol based on page protocol
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const baseUrl = (import.meta.env.VITE_WS_URL || `${protocol}//${window.location.host}`).replace(/\/$/, '');
    const wsUrl = `${baseUrl}/api/v1/ws/signaling/${sessionId}?role=broadcaster`;
    signalingSocket = new WebSocket(wsUrl);

    signalingSocket.onopen = () => {
      statusText.innerText = 'LIVE (WAITING FOR VIEWERS)';
    };

    signalingSocket.onmessage = async (event) => {
      const msg = JSON.parse(event.data);
      
      if (msg.type === 'answer') {
        if (peerConnection) {
          await peerConnection.setRemoteDescription(new RTCSessionDescription(msg));
        }
      } else if (msg.type === 'candidate') {
        if (peerConnection) {
          await peerConnection.addIceCandidate(new RTCIceCandidate(msg.candidate));
        }
      } else if (msg.type === 'viewer_connected') {
        // When a viewer connects, we need to create an offer for them
        // For simplicity in a 1-to-many setup, each viewer might need their own RTCPeerConnection.
        // But for this phase, we'll assume a 1-to-1 connection per session for the demonstration.
        createPeerConnection();
      }
    };

    signalingSocket.onclose = () => {
      statusText.innerText = 'DISCONNECTED';
      stopCamera();
    };

    // To handle initial offer, we create PC right away. If multiple viewers connect, a more complex SFU/mesh is needed.
    // For Phase 2A, we broadcast an offer to the signaling server, and any viewer can answer.
    createPeerConnection();
  }

  async function createPeerConnection() {
    if (peerConnection) {
      peerConnection.close();
    }

    peerConnection = new RTCPeerConnection(iceServers);

    // Add local tracks to peer connection
    localStream.getTracks().forEach(track => {
      peerConnection.addTrack(track, localStream);
    });

    peerConnection.onicecandidate = (event) => {
      if (event.candidate && signalingSocket && signalingSocket.readyState === WebSocket.OPEN) {
        signalingSocket.send(JSON.stringify({
          type: 'candidate',
          candidate: event.candidate
        }));
      }
    };

    peerConnection.onconnectionstatechange = () => {
      if (peerConnection.connectionState === 'connected') {
        statusText.innerText = 'LIVE (CONNECTED)';
        statusText.style.color = 'var(--success-color)';
      }
    };

    // Create Offer
    const offer = await peerConnection.createOffer();
    await peerConnection.setLocalDescription(offer);
    
    if (signalingSocket && signalingSocket.readyState === WebSocket.OPEN) {
      signalingSocket.send(JSON.stringify(peerConnection.localDescription));
    } else {
      signalingSocket.onopen = () => {
        signalingSocket.send(JSON.stringify(peerConnection.localDescription));
        statusText.innerText = 'LIVE (WAITING FOR VIEWERS)';
      }
    }
  }

  function stopCamera() {
    if (localStream) {
      localStream.getTracks().forEach(track => track.stop());
      localStream = null;
    }
    if (peerConnection) {
      peerConnection.close();
      peerConnection = null;
    }
    if (signalingSocket) {
      signalingSocket.close();
      signalingSocket = null;
    }
    if (videoPreview) {
      videoPreview.srcObject = null;
    }
    currentSessionId = null;
    statusText.innerText = 'DISCONNECTED';
  }
}
