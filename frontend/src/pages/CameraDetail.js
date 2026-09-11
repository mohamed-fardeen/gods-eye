export function renderCameraDetail() {
  return `
    <div class="page-padding page-fade" style="display: flex; flex-direction: column; gap: 20px; height: calc(100vh - 64px); overflow: hidden;">
      
      <!-- Top Toolbar -->
      <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 12px 20px; flex-shrink: 0;">
        <div style="display: flex; gap: 16px; align-items: center;">
          <button id="btn-back-cameras" class="btn btn-ghost" style="padding: 4px 8px;">← Back</button>
          <h2 id="detail-camera-title" style="font-size: 16px; font-weight: 600; color: #fff; margin: 0;">CAMERA DETAIL</h2>
        </div>
        <div style="display:flex; align-items:center; gap:6px;">
          <div class="status-indicator live"></div>
          <span style="font-size:12px; font-weight:700; color:var(--success-color); text-transform:uppercase;">Live Analysis</span>
        </div>
      </div>

      <!-- Main Layout: Side by Side -->
      <div style="display: flex; gap: 20px; flex: 1; min-height: 0;">
        
        <!-- Raw Video Side -->
        <div style="flex: 1; background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; overflow: hidden; display: flex; flex-direction: column;">
          <div style="padding: 10px 14px; border-bottom: 1px solid rgba(255,255,255,0.05); background: rgba(0,0,0,0.2);">
            <span style="font-size:12px; font-weight:700; color:#fff;">RAW FEED</span>
          </div>
          <div style="flex: 1; background: #000; position: relative;">
            <video id="raw-video-feed" playsinline loop style="width: 100%; height: 100%; object-fit: contain;"></video>
          </div>
          <!-- Controls for simulated video -->
          <div id="sim-controls" style="padding: 10px; display: flex; gap: 10px; justify-content: center; border-top: 1px solid rgba(255,255,255,0.05); display: none;">
             <button id="btn-sim-play" class="btn btn-primary" style="padding: 4px 12px; font-size: 12px;">Play</button>
             <button id="btn-sim-pause" class="btn btn-ghost" style="padding: 4px 12px; font-size: 12px;">Pause</button>
          </div>
        </div>

        <!-- AI Annotated Side -->
        <div style="flex: 1; background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; overflow: hidden; display: flex; flex-direction: column;">
          <div style="padding: 10px 14px; border-bottom: 1px solid rgba(255,255,255,0.05); background: rgba(0,0,0,0.2);">
            <span style="font-size:12px; font-weight:700; color:var(--primary-color);">REAL-TIME AI ANALYSIS (ANPR)</span>
          </div>
          <div style="flex: 1; background: #000; position: relative;">
            <img id="annotated-video-feed" style="width: 100%; height: 100%; object-fit: contain;" />
            <div id="anpr-results-overlay" style="position: absolute; bottom: 10px; left: 10px; right: 10px; background: rgba(0,0,0,0.7); color: var(--green); padding: 8px; border-radius: 4px; font-family: monospace; font-size: 14px; font-weight: bold; z-index: 10; display: none;">
              Waiting for analysis...
            </div>
          </div>
        </div>

      </div>

    </div>
  `;
}

export function initCameraDetail() {
  document.getElementById('btn-back-cameras').addEventListener('click', () => {
    window.location.hash = '#/cameras';
  });

  const urlParams = new URLSearchParams(window.location.hash.split('?')[1]);
  const camId = urlParams.get('id');
  
  const rawVideo = document.getElementById('raw-video-feed');
  const annotatedImg = document.getElementById('annotated-video-feed');
  const overlay = document.getElementById('anpr-results-overlay');
  const simControls = document.getElementById('sim-controls');
  const title = document.getElementById('detail-camera-title');

  let processInterval = null;
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');

  if (camId === 'SIM_TEST_01') {
    title.innerText = 'CAMERA: SIM_TEST_01 (License Plate Test)';
    rawVideo.src = '/videos/license_plate_test.mp4';
    simControls.style.display = 'flex';
    
    document.getElementById('btn-sim-play').addEventListener('click', () => rawVideo.play());
    document.getElementById('btn-sim-pause').addEventListener('click', () => rawVideo.pause());

    // Play by default (muted for autoplay)
    rawVideo.muted = true;
    rawVideo.play().catch(e => console.warn('Autoplay prevented', e));
  } else {
    // For a real camera, we would use WebRTC/cameraStreamManager here to attach to rawVideo
    title.innerText = `CAMERA: ${camId}`;
    overlay.style.display = 'block';
    overlay.innerText = 'Real camera streams not yet fully integrated in detail view.';
    return;
  }

  // Start ANPR processing loop
  overlay.style.display = 'block';
  
  const backendUrl = (import.meta.env.VITE_BACKEND_URL || '').replace(/\/$/, '');
  
  let processingActive = true;
  let activeRequests = 0;
  const MAX_ACTIVE = 3;

  function processFrame() {
    if (!processingActive || rawVideo.paused || rawVideo.ended || !rawVideo.videoWidth) {
      if (processingActive) {
        setTimeout(processFrame, 200);
      }
      return; 
    }
    
    if (activeRequests >= MAX_ACTIVE) {
      setTimeout(processFrame, 30);
      return;
    }
    
    activeRequests++;

    canvas.width = rawVideo.videoWidth;
    canvas.height = rawVideo.videoHeight;
    ctx.drawImage(rawVideo, 0, 0, canvas.width, canvas.height);
    
    canvas.toBlob((blob) => {
      if (!blob) {
        activeRequests--;
        if (processingActive) setTimeout(processFrame, 50);
        return;
      }
      
      // Schedule the next frame capture immediately without waiting for HTTP response!
      if (processingActive) setTimeout(processFrame, 40); 
      
      const formData = new FormData();
      formData.append('file', blob, 'frame.jpg');
      
      fetch(`${backendUrl}/api/v1/ocrtest`, {
        method: 'POST',
        body: formData
      })
      .then(res => res.json())
      .then(data => {
        if (data && data.processed_image_base64) {
           annotatedImg.src = 'data:image/jpeg;base64,' + data.processed_image_base64;
        }
        if (data && data.ocr_results && data.ocr_results.length > 0) {
          const topResult = data.ocr_results[0];
          overlay.innerText = `PLATE: ${topResult.text} (${(topResult.confidence * 100).toFixed(1)}%)`;
        } else {
          overlay.innerText = 'Scanning for plates...';
        }
      })
      .catch(err => {
        console.error("ANPR API Error:", err);
      })
      .finally(() => {
        activeRequests--;
      });
    }, 'image/jpeg', 0.6);
  }

  // Start processing loop
  processFrame();

  // Cleanup on navigate away
  const oldHashChange = window.onhashchange;
  window.onhashchange = (e) => {
    processingActive = false;
    if (oldHashChange) oldHashChange(e);
  };
}
