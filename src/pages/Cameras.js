export function renderCameras() {
  return `
    <div style="padding: 24px; display: flex; flex-direction: column; gap: 20px; flex: 1; overflow-y: auto;">
      
      <!-- Top Toolbar -->
      <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 12px 20px;">
        <div style="display: flex; gap: 16px; align-items: center;">
          <!-- Search -->
          <div style="position: relative; width: 240px;">
            <input type="text" placeholder="Search Camera..." style="width:100%; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.1); border-radius:8px; padding:8px 12px; padding-right:32px; color:#fff; font-size:12px; outline:none;">
            <svg style="position:absolute; right:10px; top:50%; transform:translateY(-50%); color:var(--text-muted);" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          </div>
          
          <!-- Dropdowns -->
          <select style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.1); border-radius:8px; padding:8px 32px 8px 12px; color:var(--text-200); font-size:12px; appearance:none; cursor:pointer;">
            <option>All Zones</option>
            <option>Zone 1</option>
            <option>Zone 2</option>
          </select>
          <select style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.1); border-radius:8px; padding:8px 32px 8px 12px; color:var(--text-200); font-size:12px; appearance:none; cursor:pointer;">
            <option>All Status</option>
            <option>Online</option>
            <option>Offline</option>
          </select>
        </div>
        
        <div style="display: flex; gap: 12px; align-items: center;">
          <!-- View Toggles -->
          <div style="display:flex; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.1); border-radius:8px; padding:4px;">
            <div style="padding:6px 12px; background:var(--blue); border-radius:4px; color:#fff; cursor:pointer;"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg></div>
            <div style="padding:6px 12px; color:var(--text-muted); cursor:pointer;"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg></div>
          </div>
          <button style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.1); border-radius:8px; padding:8px 16px; color:var(--text-200); font-size:12px; display:flex; align-items:center; gap:8px; cursor:pointer;">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"/></svg> Map View
          </button>
        </div>
      </div>

      <!-- Main Layout -->
      <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 20px; flex: 1;">
        
        <!-- Left: Camera Grid -->
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; align-content: start;">
          ${Array.from({length: 9}).map((_, i) => {
            const camNum = String(i + 1).padStart(2, '0');
            const isActive = i === 1; // Highlight CAM-02
            const isOffline = i === 7; // Offline CAM-08
            
            const titles = [
              'Anna Salai Junction', 'T. Nagar Signal', 'OMR Junction',
              'Velachery Main Rd', 'Guindy Signal', 'Adyar Bridge',
              'Anna Nagar Roundana', 'Kodambakkam Flyover', 'Saidapet Bridge'
            ];

            return `
            <div style="background: rgba(12,17,32,0.9); border: 1px solid ${isActive ? 'var(--blue)' : 'rgba(255,255,255,0.07)'}; border-radius: 12px; overflow: hidden; display: flex; flex-direction: column; ${isActive ? 'box-shadow: 0 0 0 1px var(--blue);' : ''}">
              <!-- Header -->
              <div style="padding: 10px 14px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.05); background: rgba(0,0,0,0.2);">
                <div style="display: flex; gap: 8px; align-items: center;">
                  <span style="font-size:12px; font-weight:700; color:#fff;">CAM-${camNum}</span>
                  <span style="font-size:11px; color:var(--text-muted);">${titles[i]}</span>
                </div>
                ${isOffline ? 
                  `<div style="display:flex; align-items:center; gap:6px;"><div style="width:6px; height:6px; border-radius:50%; background:var(--red);"></div><span style="font-size:10px; font-weight:700; color:var(--red); text-transform:uppercase;">Offline</span></div>` :
                  `<div style="display:flex; align-items:center; gap:6px;"><div style="width:6px; height:6px; border-radius:50%; background:var(--green); box-shadow:0 0 4px var(--green);"></div><span style="font-size:10px; font-weight:700; color:var(--green); text-transform:uppercase;">Live</span></div>`
                }
              </div>
              
              <!-- Video Area -->
              <div style="aspect-ratio: 16/9; background: ${isOffline ? 'rgba(0,0,0,0.8)' : 'rgba(0,0,0,0.5)'}; position: relative; display: flex; align-items: center; justify-content: center;">
                ${isOffline ? `
                  <div style="display:flex; flex-direction:column; align-items:center; gap:8px; color:var(--text-muted);">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="m2 2 20 20"/><path d="M10.41 10.41a2 2 0 1 1-2.83-2.83"/><path d="M13.59 13.59a2 2 0 1 1-2.83-2.83"/><path d="M17.41 17.41a2 2 0 1 1-2.83-2.83"/><path d="M9.59 9.59a2 2 0 1 1-2.83-2.83"/><path d="M15 13.06V7a2 2 0 0 0-2-2h-3.94"/><path d="M12 21h4.06l-2-2H12Z"/></svg>
                    <div style="font-size:11px; font-weight:600;">Camera Offline</div>
                    <div style="font-size:9px;">No Signal</div>
                  </div>
                ` : ``}
              </div>
              
              <!-- Footer Counts -->
              <div style="padding: 10px 14px; display: flex; gap: 16px; border-top: 1px solid rgba(255,255,255,0.05); background: rgba(0,0,0,0.2);">
                <div style="display:flex; align-items:center; gap:6px; font-size:11px; color:var(--text-200);"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 17H3a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v5h-3"/><path d="M14 17a2 2 0 1 0 4 0 2 2 0 0 0-4 0"/><path d="M5 17a2 2 0 1 0 4 0 2 2 0 0 0-4 0"/></svg> ${isOffline ? 0 : Math.floor(Math.random()*20 + 10)}</div>
                <div style="display:flex; align-items:center; gap:6px; font-size:11px; color:var(--text-200);"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="18.5" cy="17.5" r="3.5"/><circle cx="5.5" cy="17.5" r="3.5"/><circle cx="15" cy="5" r="1"/><polyline points="12 17.5 12 7 15 5"/><polyline points="5.5 17.5 12 17.5"/><line x1="12" y1="7" x2="15" y2="7"/></svg> ${isOffline ? 0 : Math.floor(Math.random()*10 + 2)}</div>
                <div style="display:flex; align-items:center; gap:6px; font-size:11px; color:var(--text-200);"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="2" y1="17" x2="22" y2="17"/><line x1="8" y1="21" x2="16" y2="21"/></svg> ${isOffline ? 0 : Math.floor(Math.random()*4)}</div>
                <div style="display:flex; align-items:center; gap:6px; font-size:11px; color:var(--text-200);"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 17h4V5H2v12h3"/><path d="M20 17h2v-3.34a4 4 0 0 0-1.17-2.83L19 9h-5"/><path d="M14 17h1"/><circle cx="7.5" cy="17.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/></svg> ${isOffline ? 0 : Math.floor(Math.random()*2)}</div>
              </div>
            </div>
            `;
          }).join('')}
        </div>

        <!-- Right: Selected Camera Details -->
        <div style="display: flex; flex-direction: column; gap: 20px;">
          
          <!-- Large Video View -->
          <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; overflow: hidden; display: flex; flex-direction: column;">
            <div style="padding: 14px 20px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.05); background: rgba(0,0,0,0.2);">
              <div style="display: flex; gap: 12px; align-items: center;">
                <span style="font-size:14px; font-weight:700; color:#fff;">CAM-02</span>
                <span style="font-size:12px; color:var(--text-muted);">T. Nagar Signal</span>
              </div>
              <div style="display: flex; gap: 16px; align-items: center;">
                <div style="display:flex; align-items:center; gap:6px;"><div style="width:6px; height:6px; border-radius:50%; background:var(--green); box-shadow:0 0 4px var(--green);"></div><span style="font-size:11px; font-weight:700; color:var(--green); text-transform:uppercase;">Live</span></div>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              </div>
            </div>
            
            <div style="aspect-ratio: 16/9; background: rgba(0,0,0,0.5);"></div>
            
            <div style="padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid rgba(255,255,255,0.05); background: rgba(0,0,0,0.2);">
              <div style="display: flex; gap: 16px; align-items: center;">
                <button style="background:var(--blue); border:none; border-radius:6px; padding:6px 12px; color:#fff; font-size:11px; font-weight:600; display:flex; align-items:center; gap:6px; cursor:pointer;"><svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"/></svg> Live</button>
                <div style="color:var(--text-200); cursor:pointer;"><svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg></div>
                <div style="color:var(--text-muted); cursor:pointer;"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg></div>
                <div style="color:var(--text-muted); cursor:pointer;"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="22"/></svg></div>
              </div>
              <div style="color:var(--text-muted); cursor:pointer;"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/></svg></div>
            </div>
          </div>

          <!-- Detections -->
          <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 16px 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
              <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">DETECTIONS (Real-time)</span>
              <span style="font-size:11px; color:var(--text-dim);">Total: 38</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
              <div style="display:flex; align-items:center; gap:8px;">
                <div style="color:var(--green);"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 17H3a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v5h-3"/><path d="M14 17a2 2 0 1 0 4 0 2 2 0 0 0-4 0"/><path d="M5 17a2 2 0 1 0 4 0 2 2 0 0 0-4 0"/></svg></div>
                <div><div style="font-size:14px; font-weight:700; color:#fff;">24</div><div style="font-size:10px; color:var(--text-dim);">Cars</div></div>
              </div>
              <div style="display:flex; align-items:center; gap:8px;">
                <div style="color:var(--amber);"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="18.5" cy="17.5" r="3.5"/><circle cx="5.5" cy="17.5" r="3.5"/><circle cx="15" cy="5" r="1"/><polyline points="12 17.5 12 7 15 5"/><polyline points="5.5 17.5 12 17.5"/><line x1="12" y1="7" x2="15" y2="7"/></svg></div>
                <div><div style="font-size:14px; font-weight:700; color:#fff;">10</div><div style="font-size:10px; color:var(--text-dim);">Bikes</div></div>
              </div>
              <div style="display:flex; align-items:center; gap:8px;">
                <div style="color:var(--purple);"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="2" y1="17" x2="22" y2="17"/><line x1="8" y1="21" x2="16" y2="21"/></svg></div>
                <div><div style="font-size:14px; font-weight:700; color:#fff;">3</div><div style="font-size:10px; color:var(--text-dim);">Buses</div></div>
              </div>
              <div style="display:flex; align-items:center; gap:8px;">
                <div style="color:var(--red);"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 17h4V5H2v12h3"/><path d="M20 17h2v-3.34a4 4 0 0 0-1.17-2.83L19 9h-5"/><path d="M14 17h1"/><circle cx="7.5" cy="17.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/></svg></div>
                <div><div style="font-size:14px; font-weight:700; color:#fff;">1</div><div style="font-size:10px; color:var(--text-dim);">Trucks</div></div>
              </div>
            </div>
          </div>

          <!-- ANPR Detections -->
          <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 16px 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
              <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">ANPR DETECTIONS</span>
              <span style="font-size:10px; color:var(--blue); cursor:pointer;">View All</span>
            </div>
            <table style="width: 100%; border-collapse: collapse; font-size: 11px;">
              <thead>
                <tr style="color:var(--text-dim); border-bottom:1px solid rgba(255,255,255,0.05);">
                  <th style="text-align:left; padding-bottom:8px; font-weight:500;">Plate Number</th>
                  <th style="text-align:left; padding-bottom:8px; font-weight:500;">Time</th>
                  <th style="text-align:left; padding-bottom:8px; font-weight:500;">Type</th>
                  <th style="text-align:right; padding-bottom:8px; font-weight:500;">Confidence</th>
                </tr>
              </thead>
              <tbody style="color:var(--text-200);">
                <tr>
                  <td style="padding: 8px 0; font-weight:600; color:#fff;">TN09AB1234</td>
                  <td style="padding: 8px 0;">12:45:30 PM</td>
                  <td style="padding: 8px 0;"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 17H3a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v5h-3"/><path d="M14 17a2 2 0 1 0 4 0 2 2 0 0 0-4 0"/><path d="M5 17a2 2 0 1 0 4 0 2 2 0 0 0-4 0"/></svg></td>
                  <td style="padding: 8px 0; text-align:right; color:var(--text-100);">96%</td>
                </tr>
                <tr>
                  <td style="padding: 8px 0; font-weight:600; color:#fff;">TN10CD5678</td>
                  <td style="padding: 8px 0;">12:45:28 PM</td>
                  <td style="padding: 8px 0;"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 17H3a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v5h-3"/><path d="M14 17a2 2 0 1 0 4 0 2 2 0 0 0-4 0"/><path d="M5 17a2 2 0 1 0 4 0 2 2 0 0 0-4 0"/></svg></td>
                  <td style="padding: 8px 0; text-align:right; color:var(--text-100);">95%</td>
                </tr>
                <tr>
                  <td style="padding: 8px 0; font-weight:600; color:#fff;">TN07EF9012</td>
                  <td style="padding: 8px 0;">12:45:25 PM</td>
                  <td style="padding: 8px 0;"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 17H3a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v5h-3"/><path d="M14 17a2 2 0 1 0 4 0 2 2 0 0 0-4 0"/><path d="M5 17a2 2 0 1 0 4 0 2 2 0 0 0-4 0"/></svg></td>
                  <td style="padding: 8px 0; text-align:right; color:var(--text-100);">94%</td>
                </tr>
                <tr>
                  <td style="padding: 8px 0; font-weight:600; color:#fff;">TN11GH3456</td>
                  <td style="padding: 8px 0;">12:45:20 PM</td>
                  <td style="padding: 8px 0;"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 17H3a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v5h-3"/><path d="M14 17a2 2 0 1 0 4 0 2 2 0 0 0-4 0"/><path d="M5 17a2 2 0 1 0 4 0 2 2 0 0 0-4 0"/></svg></td>
                  <td style="padding: 8px 0; text-align:right; color:var(--text-100);">93%</td>
                </tr>
                <tr>
                  <td style="padding: 8px 0; font-weight:600; color:#fff;">TN09IJ7890</td>
                  <td style="padding: 8px 0;">12:45:18 PM</td>
                  <td style="padding: 8px 0;"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 17H3a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v5h-3"/><path d="M14 17a2 2 0 1 0 4 0 2 2 0 0 0-4 0"/><path d="M5 17a2 2 0 1 0 4 0 2 2 0 0 0-4 0"/></svg></td>
                  <td style="padding: 8px 0; text-align:right; color:var(--text-100);">92%</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Camera Info -->
          <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 16px 20px; display: flex; flex-direction: column; flex: 1;">
            <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px; margin-bottom:16px;">CAMERA INFO</span>
            <div style="display: flex; gap: 20px; flex: 1;">
              <div style="flex:1; display:flex; flex-direction:column; gap:8px; font-size:11px;">
                <div style="display:flex;"><span style="width:100px; color:var(--text-dim);">Location</span><span style="color:var(--text-100);">T. Nagar Signal, Chennai</span></div>
                <div style="display:flex;"><span style="width:100px; color:var(--text-dim);">Zone</span><span style="color:var(--text-100);">Zone 2</span></div>
                <div style="display:flex;"><span style="width:100px; color:var(--text-dim);">Direction</span><span style="color:var(--text-100);">North-East</span></div>
                <div style="display:flex;"><span style="width:100px; color:var(--text-dim);">Status</span><span style="color:var(--green);">Online</span></div>
                <div style="display:flex;"><span style="width:100px; color:var(--text-dim);">Resolution</span><span style="color:var(--text-100);">1920 x 1080</span></div>
                <div style="display:flex;"><span style="width:100px; color:var(--text-dim);">Last Maintenance</span><span style="color:var(--text-100);">20 May 2024</span></div>
              </div>
              <!-- Mini map representation -->
              <div style="width:120px; background:#000; border:1px solid rgba(255,255,255,0.1); border-radius:8px; position:relative; overflow:hidden;">
                <!-- grid background to look like a map -->
                <div style="position:absolute; inset:0; opacity:0.2; background-image: linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px); background-size: 20px 20px;"></div>
                <svg style="position:absolute; inset:0; width:100%; height:100%; opacity:0.5;" stroke="var(--blue)" stroke-width="2" fill="none"><path d="M-10,40 L60,10 L140,80" /><path d="M40,-10 L80,130" /></svg>
                <div style="position:absolute; top:40%; left:60%; transform:translate(-50%, -50%); color:var(--blue);"><svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="1"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3" fill="#000"/></svg></div>
              </div>
            </div>
          </div>
        </div>

      </div>

    </div>
  `;
}
