export function renderOcrTest() {
  return `<div class="page-padding page-fade" style="max-width:1000px;margin:0 auto;width:100%;">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
      <div>
        <h2 style="margin:0;font-size:18px;">Pipeline Test (Phase 2B)</h2>
        <div style="font-size:12px;color:var(--text-muted);margin-top:4px;">Test the AI Worker inference pipeline with custom images</div>
      </div>
      <div id="ai-worker-status-badge" class="badge">Checking AI Worker...</div>
    </div>

    <div style="display:grid;grid-template-columns:300px 1fr;gap:20px;">
      
      <!-- Upload Panel -->
      <div class="panel">
        <div class="panel-hdr"><span class="panel-title">Input</span></div>
        <div class="panel-body">
          <div id="drop-zone" style="border:2px dashed var(--border);border-radius:6px;padding:30px 20px;text-align:center;cursor:pointer;transition:all 0.2s;background:var(--bg-900);">
            <div style="color:var(--text-muted);margin-bottom:10px;">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
            </div>
            <div style="font-size:13px;font-weight:600;margin-bottom:4px;">Drag & Drop Image</div>
            <div style="font-size:11px;color:var(--text-dim);">or click to browse</div>
            <input type="file" id="file-input" accept="image/*" style="display:none;">
          </div>

          <button id="run-inference-btn" class="btn btn-primary" style="width:100%;margin-top:15px;display:none;">
            Run Inference
          </button>

          <div id="preview-container" style="margin-top:15px;display:none;">
            <div style="font-size:11px;color:var(--text-muted);margin-bottom:4px;">Input Preview</div>
            <img id="image-preview" style="width:100%;border-radius:4px;border:1px solid var(--border);" />
          </div>
        </div>
      </div>

      <!-- Results Panel -->
      <div class="panel">
        <div class="panel-hdr"><span class="panel-title">Inference Results</span></div>
        <div class="panel-body" style="min-height:300px;display:flex;flex-direction:column;">
          
          <div id="results-placeholder" style="flex:1;display:flex;align-items:center;justify-content:center;color:var(--text-dim);font-size:13px;">
            Upload an image to see results
          </div>

          <div id="results-content" style="display:none;">
            <div style="display:grid;grid-template-columns:2fr 1fr;gap:20px;margin-bottom:20px;">
              <div>
                <img id="result-image" style="width:100%;border-radius:4px;border:1px solid var(--border);" />
              </div>
              <div>
                <div style="font-size:12px;font-weight:600;margin-bottom:8px;color:var(--text-muted);text-transform:uppercase;">Counts</div>
                <div style="background:var(--bg-900);padding:10px;border-radius:4px;border:1px solid var(--border);margin-bottom:15px;">
                  <div style="display:flex;justify-content:space-between;margin-bottom:4px;font-size:13px;">
                    <span style="color:var(--text-dim);">Vehicles</span><span id="res-vehicles" style="font-weight:600;color:var(--cyan);">0</span>
                  </div>
                  <div style="display:flex;justify-content:space-between;margin-bottom:4px;font-size:13px;">
                    <span style="color:var(--text-dim);">Plates Detected</span><span id="res-plates" style="font-weight:600;">0</span>
                  </div>
                  <div style="display:flex;justify-content:space-between;font-size:13px;">
                    <span style="color:var(--text-dim);">Plates Read</span><span id="res-reads" style="font-weight:600;color:var(--green);">0</span>
                  </div>
                </div>

                <div style="font-size:12px;font-weight:600;margin-bottom:8px;color:var(--text-muted);text-transform:uppercase;">Detected Plates</div>
                <div id="plates-list" style="display:flex;flex-direction:column;gap:6px;max-height:200px;overflow-y:auto;">
                </div>
              </div>
            </div>

            <!-- Timings Table -->
            <div style="font-size:12px;font-weight:600;margin-bottom:8px;color:var(--text-muted);text-transform:uppercase;">Pipeline Checkpoints</div>
            <table style="width:100%;font-size:12px;border-collapse:collapse;">
              <thead>
                <tr style="border-bottom:1px solid var(--border);color:var(--text-dim);">
                  <th style="text-align:left;padding:6px 0;">Stage</th>
                  <th style="text-align:right;padding:6px 0;">Time (ms)</th>
                </tr>
              </thead>
              <tbody id="timings-tbody">
              </tbody>
            </table>
          </div>
        </div>
      </div>

    </div>
  </div>`;
}

export function initOcrTest() {
  const dropZone = document.getElementById('drop-zone');
  const fileInput = document.getElementById('file-input');
  const previewContainer = document.getElementById('preview-container');
  const imagePreview = document.getElementById('image-preview');
  const runBtn = document.getElementById('run-inference-btn');
  const statusBadge = document.getElementById('ai-worker-status-badge');
  
  const resultsPlaceholder = document.getElementById('results-placeholder');
  const resultsContent = document.getElementById('results-content');
  const resultImage = document.getElementById('result-image');
  const resVehicles = document.getElementById('res-vehicles');
  const resPlates = document.getElementById('res-plates');
  const resReads = document.getElementById('res-reads');
  const platesList = document.getElementById('plates-list');
  const timingsTbody = document.getElementById('timings-tbody');

  let selectedFile = null;

  // Check worker status
  fetch('http://localhost:8000/api/v1/settings/ai-worker')
    .then(res => res.json())
    .then(data => {
      if (data.connected && data.models_loaded) {
        statusBadge.className = 'badge online';
        statusBadge.innerText = 'AI Worker Ready';
      } else {
        statusBadge.className = 'badge offline';
        statusBadge.innerText = 'AI Worker Unavailable';
        runBtn.disabled = true;
      }
    })
    .catch(() => {
      statusBadge.className = 'badge offline';
      statusBadge.innerText = 'Backend Unreachable';
      runBtn.disabled = true;
    });

  dropZone.addEventListener('click', () => fileInput.click());
  
  dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = 'var(--blue)';
    dropZone.style.background = 'rgba(59, 130, 246, 0.05)';
  });

  dropZone.addEventListener('dragleave', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = 'var(--border)';
    dropZone.style.background = 'var(--bg-900)';
  });

  dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = 'var(--border)';
    dropZone.style.background = 'var(--bg-900)';
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFile(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener('change', (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFile(e.target.files[0]);
    }
  });

  function handleFile(file) {
    if (!file.type.startsWith('image/')) {
      alert('Please upload an image file.');
      return;
    }
    selectedFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
      imagePreview.src = e.target.result;
      previewContainer.style.display = 'block';
      runBtn.style.display = 'block';
      resultsPlaceholder.style.display = 'flex';
      resultsContent.style.display = 'none';
    };
    reader.readAsDataURL(file);
  }

  runBtn.addEventListener('click', () => {
    if (!selectedFile) return;

    runBtn.disabled = true;
    runBtn.innerText = 'Processing...';
    resultsPlaceholder.style.display = 'flex';
    resultsPlaceholder.innerHTML = '<div class="spinner" style="width:20px;height:20px;border:2px solid var(--blue);border-top-color:transparent;border-radius:50%;animation:spin 1s linear infinite;"></div><span style="margin-left:10px;">Running inference...</span>';
    resultsContent.style.display = 'none';

    const formData = new FormData();
    formData.append('file', selectedFile);

    fetch('http://localhost:8000/api/v1/ocrtest', {
      method: 'POST',
      body: formData
    })
    .then(res => {
      if (!res.ok) throw new Error('Inference failed');
      return res.json();
    })
    .then(data => {
      runBtn.disabled = false;
      runBtn.innerText = 'Run Inference';
      
      resultsPlaceholder.style.display = 'none';
      resultsContent.style.display = 'block';

      resultImage.src = 'data:image/jpeg;base64,' + data.processed_image_base64;
      
      resVehicles.innerText = data.counts.vehicles_detected;
      resPlates.innerText = data.counts.plates_detected;
      resReads.innerText = data.counts.successful_ocr;

      // Render Plates
      platesList.innerHTML = data.ocr_results.map(r => `
        <div style="background:var(--bg-800);border:1px solid var(--border);padding:6px 10px;border-radius:4px;display:flex;justify-content:space-between;align-items:center;">
          <span style="font-family:monospace;font-size:14px;font-weight:700;color:var(--text-100);">${r.text}</span>
          <span style="font-size:11px;color:var(--text-muted);">${(r.confidence * 100).toFixed(1)}% | ${r.variant}</span>
        </div>
      `).join('');

      if (data.ocr_results.length === 0) {
        platesList.innerHTML = '<div style="font-size:11px;color:var(--text-dim);font-style:italic;">No plates read</div>';
      }

      // Render Timings
      timingsTbody.innerHTML = Object.entries(data.checkpoints).map(([stage, time]) => `
        <tr style="border-bottom:1px solid var(--border-light);">
          <td style="padding:6px 0;">${stage}</td>
          <td style="text-align:right;padding:6px 0;font-family:monospace;">${time} ms</td>
        </tr>
      `).join('');
    })
    .catch(err => {
      runBtn.disabled = false;
      runBtn.innerText = 'Run Inference';
      resultsPlaceholder.innerHTML = `<span style="color:var(--red);">Error: ${err.message}</span>`;
    });
  });
}
