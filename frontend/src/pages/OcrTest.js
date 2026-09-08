export function renderOcrTest() {
  return `<div class="page-padding page-fade" style="max-width:1000px;margin:0 auto;width:100%;">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
      <div>
        <h2 style="margin:0;font-size:18px;">Live Video Simulation</h2>
        <div style="font-size:12px;color:var(--text-muted);margin-top:4px;">Upload multiple videos with location & time to test multi-camera tracking</div>
      </div>
    </div>

    <div class="panel" style="margin-bottom: 20px;">
      <div class="panel-hdr"><span class="panel-title">Simulation Inputs</span></div>
      <div class="panel-body">
        <div id="video-inputs-container">
          <!-- Dynamic inputs will be appended here -->
        </div>
        
        <button id="add-video-btn" class="btn btn-secondary" style="margin-top: 15px;">
          + Add Camera Video
        </button>
      </div>
    </div>

    <button id="start-sim-btn" class="btn btn-primary" style="width:100%; padding: 12px; font-size: 14px;">
      Start Simulation
    </button>

    <div id="sim-results" style="margin-top:20px; display:none;">
      <div class="panel">
        <div class="panel-hdr"><span class="panel-title">Status</span></div>
        <div class="panel-body" id="sim-status-content" style="font-family: monospace; font-size: 13px;">
        </div>
      </div>
    </div>
  </div>`;
}

export function initOcrTest() {
  const container = document.getElementById('video-inputs-container');
  const addBtn = document.getElementById('add-video-btn');
  const startBtn = document.getElementById('start-sim-btn');
  const simResults = document.getElementById('sim-results');
  const simStatus = document.getElementById('sim-status-content');

  let videoCount = 0;

  function addVideoRow() {
    videoCount++;
    const rowId = `vid-row-${videoCount}`;
    
    const div = document.createElement('div');
    div.id = rowId;
    div.style.cssText = "background: var(--bg-900); border: 1px solid var(--border); padding: 15px; border-radius: 6px; margin-bottom: 10px;";
    
    div.innerHTML = `
      <div style="display:flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
        <span style="font-weight: 600; font-size: 13px;">Camera Source ${videoCount}</span>
        ${videoCount > 1 ? `<button type="button" class="btn-remove" data-row="${rowId}" style="background:transparent; border:none; color:var(--red); cursor:pointer; font-size:12px;">Remove</button>` : ''}
      </div>
      <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 15px;">
        <div>
          <label style="display:block; font-size:11px; color:var(--text-muted); margin-bottom:4px;">Video File</label>
          <input type="file" accept="video/mp4,video/x-m4v,video/*" class="sim-file" style="width:100%; font-size:12px; padding: 6px;">
        </div>
        <div>
          <label style="display:block; font-size:11px; color:var(--text-muted); margin-bottom:4px;">Latitude</label>
          <input type="number" step="0.0001" class="sim-lat" placeholder="13.06" style="width:100%; background:var(--bg-800); border:1px solid var(--border); color:white; padding:6px; border-radius:4px;">
        </div>
        <div>
          <label style="display:block; font-size:11px; color:var(--text-muted); margin-bottom:4px;">Longitude</label>
          <input type="number" step="0.0001" class="sim-lon" placeholder="80.25" style="width:100%; background:var(--bg-800); border:1px solid var(--border); color:white; padding:6px; border-radius:4px;">
        </div>
        <div>
          <label style="display:block; font-size:11px; color:var(--text-muted); margin-bottom:4px;">Start Time (Optional)</label>
          <input type="datetime-local" class="sim-time" style="width:100%; background:var(--bg-800); border:1px solid var(--border); color:white; padding:6px; border-radius:4px;">
        </div>
      </div>
    `;
    
    container.appendChild(div);
    
    if (videoCount > 1) {
      div.querySelector('.btn-remove').addEventListener('click', (e) => {
        document.getElementById(e.target.dataset.row).remove();
      });
    }
  }

  // Init with 2 rows by default
  addVideoRow();
  addVideoRow();

  addBtn.addEventListener('click', () => {
    addVideoRow();
  });

  startBtn.addEventListener('click', () => {
    const rows = container.children;
    const formData = new FormData();
    const metadata = [];
    
    let hasFiles = false;

    for (let i = 0; i < rows.length; i++) {
      const row = rows[i];
      const fileInput = row.querySelector('.sim-file');
      
      if (fileInput.files.length > 0) {
        hasFiles = true;
        formData.append('videos', fileInput.files[0]);
        
        const lat = parseFloat(row.querySelector('.sim-lat').value) || 0.0;
        const lon = parseFloat(row.querySelector('.sim-lon').value) || 0.0;
        const timeVal = row.querySelector('.sim-time').value;
        
        let timestamp = null;
        if (timeVal) {
          timestamp = new Date(timeVal).toISOString();
        }

        metadata.push({ lat, lon, timestamp });
      }
    }

    if (!hasFiles) {
      alert('Please upload at least one video to start simulation.');
      return;
    }

    formData.append('metadata', JSON.stringify(metadata));

    startBtn.disabled = true;
    startBtn.innerText = 'Uploading & Starting...';
    simResults.style.display = 'block';
    simStatus.innerHTML = '<span style="color:var(--yellow);">Uploading videos to backend...</span>';

    fetch('http://localhost:8000/api/v1/simulation/start_multi', {
      method: 'POST',
      body: formData
    })
    .then(res => res.json())
    .then(data => {
      startBtn.disabled = false;
      startBtn.innerText = 'Start Simulation';
      
      let html = `<span style="color:var(--green);">Success! Simulation pipelines started.</span><br><br>`;
      if (data.results) {
        data.results.forEach(r => {
          if (r.status === 'started') {
            html += `Camera <span style="color:var(--cyan);">${r.camera_id}</span> : Started<br>`;
          } else {
            html += `<span style="color:var(--red);">Camera ${r.camera_id} Failed: ${r.error}</span><br>`;
          }
        });
      }
      html += `<br><span style="color:var(--text-muted);">Switch to the Dashboard or Map view to see vehicles tracked live!</span>`;
      simStatus.innerHTML = html;
    })
    .catch(err => {
      startBtn.disabled = false;
      startBtn.innerText = 'Start Simulation';
      simStatus.innerHTML = `<span style="color:var(--red);">Error: ${err.message}</span>`;
    });
  });
}
