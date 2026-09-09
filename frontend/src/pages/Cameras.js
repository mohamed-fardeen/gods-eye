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

import { cameraStreamManager } from '../services/CameraStreamManager.js';

export function initCameras() {
  const container = document.getElementById('live-cameras-container');
  const noCamerasMsg = document.getElementById('no-cameras-message');
  const refreshBtn = document.getElementById('refresh-cameras-btn');

  async function renderFeeds() {
    container.innerHTML = '';
    const sessions = await cameraStreamManager.getLiveSessions();
    
    // Inject our simulated camera for testing
    const simulatedSession = {
      session_id: 'SIM_TEST_01',
      name: 'License Plate Detection Test (Simulated)'
    };
    const allSessions = [simulatedSession, ...sessions];
    
    if (allSessions.length === 0) {
      noCamerasMsg.style.display = 'block';
      return;
    }

    noCamerasMsg.style.display = 'none';

    allSessions.forEach(session => {
      const camDiv = document.createElement('div');
      camDiv.style.cursor = 'pointer'; // Make it look clickable
      const isSimulated = session.session_id === 'SIM_TEST_01';
      const shortId = isSimulated ? 'SIM-TEST' : `CAM-${session.session_id.substring(0, 4).toUpperCase()}`;
      
      camDiv.innerHTML = `
        <div class="camera-card" style="background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; overflow: hidden; display: flex; flex-direction: column; transition: transform 0.2s; ">
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
            ${isSimulated ? 
              `<video id="video-${session.session_id}" src="/videos/license_plate_test.mp4" loop muted autoplay playsinline style="width: 100%; height: 100%; object-fit: cover;"></video>` : 
              `<video id="video-${session.session_id}" autoplay muted playsinline style="width: 100%; height: 100%; object-fit: cover;"></video>`
            }
          </div>
        </div>
      `;
      
      // Navigate to detailed view on click
      camDiv.addEventListener('click', () => {
        window.location.hash = `#/camera-detail?id=${session.session_id}`;
      });

      // Hover effect
      camDiv.addEventListener('mouseenter', () => { camDiv.firstElementChild.style.border = '1px solid var(--primary-color)'; });
      camDiv.addEventListener('mouseleave', () => { camDiv.firstElementChild.style.border = '1px solid rgba(255,255,255,0.07)'; });

      container.appendChild(camDiv);

      if (!isSimulated) {
        const videoEl = document.getElementById(`video-${session.session_id}`);
        cameraStreamManager.connectToSession(session.session_id, videoEl);
      }
    });
  }

  refreshBtn.addEventListener('click', renderFeeds);
  renderFeeds();
}
