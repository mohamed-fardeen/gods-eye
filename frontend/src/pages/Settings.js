export function renderSettings() {
  return `<div class="page-padding page-fade" style="max-width:900px;margin:0 auto;width:100%;">

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">

      <!-- Platform Info -->
      <div class="panel">
        <div class="panel-hdr"><span class="panel-title">Platform Configuration</span></div>
        <div class="panel-body">
          <div class="data-row"><span class="data-key">Platform Name</span><span class="data-val">God's Eye Command Center</span></div>
          <div class="data-row"><span class="data-key">City</span><span class="data-val">Chennai, Tamil Nadu</span></div>
          <div class="data-row"><span class="data-key">Environment</span><span class="data-val">Development</span></div>
          <div class="data-row"><span class="data-key">Version</span><span class="data-val">1.0.0</span></div>
          <div class="data-row"><span class="data-key">Build</span><span class="data-val">2024.05.21</span></div>
          <div class="data-row" style="border:none;"><span class="data-key">Timezone</span><span class="data-val">IST (UTC +5:30)</span></div>
        </div>
      </div>

      <!-- AI Inference Worker -->
      <div class="panel" style="border:1px solid var(--blue);">
        <div class="panel-hdr" style="background:rgba(59, 130, 246, 0.1);"><span class="panel-title">AI Inference Worker</span></div>
        <div class="panel-body">
          <div style="margin-bottom: 12px;">
            <label style="font-size:12px;color:var(--text-muted);display:block;margin-bottom:4px;">Inference Mode</label>
            <select id="ai-worker-mode" class="select-input" style="width:100%;">
              <option value="LOCAL">LOCAL (Run on this computer)</option>
              <option value="REMOTE" disabled>REMOTE (Cloud GPU - Coming Later)</option>
            </select>
          </div>
          <div id="ai-worker-url-container" style="margin-bottom: 12px; display: none;">
            <label style="font-size:12px;color:var(--text-muted);display:block;margin-bottom:4px;">AI Worker URL</label>
            <input id="ai-worker-url" type="text" class="search-input" style="width:100%;" placeholder="http://127.0.0.1:8001">
          </div>
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <div id="ai-worker-status" style="font-size:12px;display:flex;flex-direction:column;gap:4px;">
              <div>Status: <span style="color:var(--amber);">Checking...</span></div>
            </div>
            <button id="ai-worker-save" class="btn btn-primary" style="padding:4px 12px;font-size:12px;">Save & Apply</button>
          </div>
        </div>
      </div>

      <!-- Cesium Map Engine -->
      <div class="panel">
        <div class="panel-hdr"><span class="panel-title">Map Engine (Cesium)</span></div>
        <div class="panel-body">
          <div class="data-row"><span class="data-key">3D Engine</span><span class="data-val" style="color:var(--cyan);">CesiumJS</span></div>
          <div class="data-row"><span class="data-key">Cesium Ion Token</span><span class="data-val" style="color:var(--text-muted);">Loaded via .env.local</span></div>
          <div class="data-row"><span class="data-key">Terrain Provider</span><span class="data-val">Cesium World Terrain</span></div>
          <div class="data-row"><span class="data-key">Base Imagery</span><span class="data-val">Aerial with Labels</span></div>
          <div class="data-row"><span class="data-key">Buildings</span><span class="data-val">Cesium OSM Buildings</span></div>
          <div class="data-row" style="border:none;"><span class="data-key">Road Provider</span><span class="data-val">Overpass API</span></div>
        </div>
      </div>

      <!-- Developer Notes -->
      <div class="panel">
        <div class="panel-hdr"><span class="panel-title">Developer Notes</span></div>
        <div class="panel-body">
          <div style="font-size:12px;color:var(--text-dim);line-height:1.8;">
            <div style="display:flex;gap:8px;align-items:flex-start;padding:6px 0;border-bottom:1px solid var(--border);">
              <span style="color:var(--green);margin-top:2px;">●</span>
              <span><strong style="color:var(--text-100);">AI Worker Architecture:</strong> Heavy computer vision (YOLO, OCR) is isolated in a separate container/service to prevent blocking the main FastAPI event loop.</span>
            </div>
            <div style="display:flex;gap:8px;align-items:flex-start;padding:6px 0;border-bottom:1px solid var(--border);">
              <span style="color:var(--green);margin-top:2px;">●</span>
              <span><strong style="color:var(--text-100);">Spatial Foundation:</strong> Interactive 3D map with OSM buildings, road network, and bridge geometry is fully operational.</span>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>`;
}

export function initSettings() {
  const modeSelect = document.getElementById('ai-worker-mode');
  const urlInput = document.getElementById('ai-worker-url');
  const statusDiv = document.getElementById('ai-worker-status');
  const saveBtn = document.getElementById('ai-worker-save');

  // Load current settings from backend
  fetch('http://localhost:8000/api/v1/settings/ai-worker')
    .then(res => res.json())
    .then(data => {
      modeSelect.value = data.mode || 'LOCAL';
      urlInput.value = data.url || 'http://localhost:8001';
      
      let statusHtml = `<div>Status: <span style="${data.connected ? 'color:var(--green);' : 'color:var(--red);'}">${data.connected ? 'CONNECTED' : 'DISCONNECTED'}</span></div>`;
      if (data.connected) {
        statusHtml += `<div>Device: <span style="color:var(--cyan);">${(data.device || '').toUpperCase()}</span></div>`;
        if (data.gpu) {
          statusHtml += `<div>GPU: <span style="color:var(--text-100);">${data.gpu}</span></div>`;
        }
        statusHtml += `<div>Models: <span style="${data.models_loaded ? 'color:var(--green);' : 'color:var(--amber);'}">${data.models_loaded ? 'LOADED' : 'NOT LOADED'}</span></div>`;
      }
      statusDiv.innerHTML = statusHtml;
    })
    .catch(err => {
      statusDiv.innerHTML = `<div>Status: <span style="color:var(--red);">API UNREACHABLE</span></div>`;
    });

  saveBtn.addEventListener('click', () => {
    saveBtn.innerText = 'Saving...';
    fetch('http://localhost:8000/api/v1/settings/ai-worker', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        mode: modeSelect.value,
        url: urlInput.value
      })
    })
    .then(res => res.json())
    .then(() => {
      saveBtn.innerText = 'Saved!';
      setTimeout(() => {
        saveBtn.innerText = 'Save & Apply';
        initSettings(); // Reload to fetch connection status
      }, 1000);
    });
  });
}
