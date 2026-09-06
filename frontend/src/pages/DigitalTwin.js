import { flyToLandmark } from "../cesium/camera.js";

export function renderDigitalTwin() {
  return `
    <div class="map-overlay-container" style="position:absolute; inset:0; pointer-events:none; display:flex; flex-direction:column; justify-content:space-between; padding:24px;">
      
      <!-- TOP OVERLAYS -->
      <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <!-- Top Left: Title -->
        <div style="pointer-events:auto; display:flex; flex-direction:column; gap:4px; text-shadow:0 1px 4px rgba(0,0,0,0.8);">
          <div style="font-size:14px; font-weight:800; color:#fff; letter-spacing:1px; text-transform:uppercase;">CHENNAI CITY</div>
          <div style="font-size:10px; font-weight:600; color:var(--text-200); letter-spacing:0.5px; text-transform:uppercase;">3D DIGITAL TWIN</div>
        </div>

        <!-- Top Center: Search -->
        <div style="pointer-events:auto; position:absolute; left:50%; transform:translateX(-50%); width:380px;">
          <div style="position:relative; width:100%;">
            <input type="text" placeholder="Search location, camera, or place" style="width:100%; background:rgba(8,12,20,0.85); backdrop-filter:blur(10px); border:1px solid rgba(255,255,255,0.1); border-radius:24px; padding:12px 20px; padding-left:44px; color:#fff; font-size:13px; font-family:inherit; outline:none; box-shadow:0 4px 12px rgba(0,0,0,0.3); transition:border-color 0.2s;">
            <svg style="position:absolute; left:16px; top:50%; transform:translateY(-50%); color:var(--text-muted);" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            <svg style="position:absolute; right:16px; top:50%; transform:translateY(-50%); color:var(--text-muted);" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
          </div>
        </div>

        <!-- Top Right: Navigation controls -->
        <div style="pointer-events:auto; display:flex; flex-direction:column; gap:10px;">
          <div style="background:rgba(8,12,20,0.85); backdrop-filter:blur(10px); border:1px solid rgba(255,255,255,0.1); border-radius:24px; width:40px; height:40px; display:flex; align-items:center; justify-content:center; cursor:pointer; box-shadow:0 4px 12px rgba(0,0,0,0.3);">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color:var(--text-100);"><polygon points="12 2 15 12 12 22 9 12 12 2" fill="var(--red)" stroke="none"/><polygon points="12 12 15 12 12 22 9 12" fill="#fff" stroke="none"/></svg>
          </div>
          <div style="background:rgba(8,12,20,0.85); backdrop-filter:blur(10px); border:1px solid rgba(255,255,255,0.1); border-radius:20px; width:40px; display:flex; flex-direction:column; padding:8px 0; gap:12px; align-items:center; box-shadow:0 4px 12px rgba(0,0,0,0.3);">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color:var(--text-200); cursor:pointer;"><path d="M18.36 6.64A9 9 0 0 1 20 7.73"/><path d="M22 12c0 5.52-4.48 10-10 10S2 17.52 2 12 6.48 2 12 2h.01"/><path d="M9 13l3-3 3 3"/></svg>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color:var(--text-200); cursor:pointer;"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>
            <div style="font-size:11px; font-weight:700; color:var(--text-200); cursor:pointer;">2D</div>
            <div style="width:20px; height:1px; background:rgba(255,255,255,0.1);"></div>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color:var(--text-200); cursor:pointer;"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color:var(--text-200); cursor:pointer;"><line x1="5" y1="12" x2="19" y2="12"/></svg>
          </div>
        </div>
      </div>

      <!-- RIGHT SIDEBAR (Selected Object) -->
      <div style="pointer-events:auto; position:absolute; right:70px; top:24px; bottom:24px; width:340px; background:rgba(12,17,32,0.95); backdrop-filter:blur(14px); border:1px solid rgba(255,255,255,0.07); border-radius:12px; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 8px 32px rgba(0,0,0,0.5);">
        <!-- Header -->
        <div style="padding:16px 20px; border-bottom:1px solid rgba(255,255,255,0.07); display:flex; justify-content:space-between; align-items:center;">
          <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">SELECTED OBJECT</span>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color:var(--text-muted); cursor:pointer;"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </div>
        
        <!-- Tabs -->
        <div style="display:flex; border-bottom:1px solid rgba(255,255,255,0.07);">
          <div style="flex:1; text-align:center; padding:12px 0; font-size:12px; font-weight:600; color:#fff; border-bottom:2px solid var(--blue); cursor:pointer;">Vehicle</div>
          <div style="flex:1; text-align:center; padding:12px 0; font-size:12px; font-weight:500; color:var(--text-muted); cursor:pointer;">Camera</div>
          <div style="flex:1; text-align:center; padding:12px 0; font-size:12px; font-weight:500; color:var(--text-muted); cursor:pointer;">Incident</div>
        </div>

        <div style="padding:20px; flex:1; overflow-y:auto; display:flex; flex-direction:column; gap:24px;">
          
          <!-- Vehicle Profile -->
          <div>
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:16px;">
              <div style="font-size:18px; font-weight:800; color:var(--cyan); letter-spacing:1px;">TN09AB1234</div>
              <div style="background:var(--green-dim); color:var(--green); border:1px solid rgba(34,197,94,0.3); font-size:10px; font-weight:700; padding:2px 8px; border-radius:4px; text-transform:uppercase;">Tracked</div>
            </div>
            <div style="display:flex; gap:16px;">
              <div style="width:100px; height:70px; background:#111827; border-radius:6px; border:1px solid rgba(255,255,255,0.1); display:flex; align-items:center; justify-content:center;">
                <!-- Car placeholder -->
                <svg width="60" height="36" viewBox="0 0 60 36" fill="none" stroke="#e2e8f0" stroke-width="1.5"><rect x="8" y="8" width="44" height="20" rx="4"/><path d="M12 8 L18 2 L42 2 L48 8" /><circle cx="18" cy="30" r="5"/><circle cx="42" cy="30" r="5"/></svg>
              </div>
              <div style="flex:1; display:flex; flex-direction:column; gap:8px;">
                <div style="display:flex; justify-content:space-between; font-size:12px;"><span style="color:var(--text-muted);">Type</span><span style="color:#fff; font-weight:500;">Sedan</span></div>
                <div style="display:flex; justify-content:space-between; font-size:12px;"><span style="color:var(--text-muted);">Color</span><span style="color:#fff; font-weight:500;">White</span></div>
                <div style="display:flex; justify-content:space-between; font-size:12px;"><span style="color:var(--text-muted);">Confidence</span><span style="color:var(--green); font-weight:600;">96%</span></div>
              </div>
            </div>
          </div>

          <!-- Vehicle Journey -->
          <div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
              <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">VEHICLE JOURNEY</span>
              <span style="font-size:11px; color:var(--blue); cursor:pointer;">View Full History</span>
            </div>
            <div style="display:flex; flex-direction:column; gap:10px; position:relative;">
              <div style="position:absolute; left:4px; top:8px; bottom:8px; width:2px; background:rgba(255,255,255,0.1);"></div>
              <div style="display:flex; gap:12px; align-items:flex-start; position:relative;">
                <div style="width:10px; height:10px; border-radius:50%; background:var(--green); box-shadow:0 0 6px var(--green); margin-top:3px; z-index:1;"></div>
                <div style="flex:1; display:flex; justify-content:space-between; font-size:11px;">
                  <span style="color:var(--text-200);">12:42:18 PM</span><span style="color:var(--cyan);">CAM-05</span><span style="color:var(--text-muted);">T. Nagar</span>
                </div>
              </div>
              <div style="display:flex; gap:12px; align-items:flex-start; position:relative;">
                <div style="width:10px; height:10px; border-radius:50%; background:var(--text-muted); margin-top:3px; z-index:1; border:2px solid #0c1120;"></div>
                <div style="flex:1; display:flex; justify-content:space-between; font-size:11px;">
                  <span style="color:var(--text-200);">12:31:47 PM</span><span style="color:var(--cyan);">CAM-03</span><span style="color:var(--text-muted);">Anna Nagar</span>
                </div>
              </div>
              <div style="display:flex; gap:12px; align-items:flex-start; position:relative;">
                <div style="width:10px; height:10px; border-radius:50%; background:var(--text-muted); margin-top:3px; z-index:1; border:2px solid #0c1120;"></div>
                <div style="flex:1; display:flex; justify-content:space-between; font-size:11px;">
                  <span style="color:var(--text-200);">12:18:02 PM</span><span style="color:var(--cyan);">CAM-01</span><span style="color:var(--text-muted);">Kilpauk</span>
                </div>
              </div>
              <div style="display:flex; gap:12px; align-items:flex-start; position:relative;">
                <div style="width:10px; height:10px; border-radius:50%; background:var(--text-muted); margin-top:3px; z-index:1; border:2px solid #0c1120;"></div>
                <div style="flex:1; display:flex; justify-content:space-between; font-size:11px;">
                  <span style="color:var(--text-200);">12:05:33 PM</span><span style="color:var(--cyan);">CAM-18</span><span style="color:var(--text-muted);">Harbour</span>
                </div>
              </div>
              <div style="display:flex; gap:12px; align-items:flex-start; position:relative;">
                <div style="width:10px; height:10px; border-radius:50%; background:var(--text-muted); margin-top:3px; z-index:1; border:2px solid #0c1120;"></div>
                <div style="flex:1; display:flex; justify-content:space-between; font-size:11px;">
                  <span style="color:var(--text-200);">11:52:11 AM</span><span style="color:var(--cyan);">CAM-21</span><span style="color:var(--text-muted);">Besant Nagar</span>
                </div>
              </div>
            </div>
            <div style="text-align:center; margin-top:12px;">
              <span style="font-size:11px; color:var(--blue); cursor:pointer;">Show on Map</span>
            </div>
          </div>

          <!-- Live Camera Preview -->
          <div>
            <div style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px; margin-bottom:12px;">LIVE CAMERA PREVIEW</div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
              <span style="font-size:12px; color:var(--text-200);">CAM-05 - T. Nagar</span>
              <span style="background:var(--red-dim); color:var(--red); border:1px solid rgba(239,68,68,0.3); font-size:9px; font-weight:700; padding:1px 6px; border-radius:3px;">LIVE</span>
            </div>
            <div style="height:120px; background:#000; border-radius:6px; border:1px solid rgba(255,255,255,0.1); position:relative; overflow:hidden;">
              <!-- Simulated traffic feed -->
              <div style="position:absolute; inset:0; background:linear-gradient(180deg, #1e293b 0%, #0f172a 100%); display:flex; align-items:center; justify-content:center;">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="color:rgba(255,255,255,0.2);"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
              </div>
              <div style="position:absolute; bottom:8px; left:8px; background:rgba(0,0,0,0.7); color:#fff; font-size:9px; padding:2px 6px; border-radius:3px; font-family:monospace;">12:45:30 PM</div>
              <div style="position:absolute; bottom:8px; right:8px; display:flex; gap:4px;">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/></svg>
              </div>
            </div>
          </div>

          <!-- Location Info -->
          <div>
            <div style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px; margin-bottom:12px;">LOCATION INFO</div>
            <div style="display:flex; flex-direction:column; gap:8px;">
              <div style="display:flex; justify-content:space-between; font-size:11px;"><span style="color:var(--text-muted);">Area</span><span style="color:#fff;">T. Nagar</span></div>
              <div style="display:flex; justify-content:space-between; font-size:11px;"><span style="color:var(--text-muted);">Zone</span><span style="color:#fff;">Zone 3</span></div>
              <div style="display:flex; justify-content:space-between; font-size:11px;"><span style="color:var(--text-muted);">Coordinates</span><span style="color:#fff;">13.0410° N, 80.2345° E</span></div>
              <div style="display:flex; justify-content:space-between; font-size:11px;"><span style="color:var(--text-muted);">Type</span><span style="color:#fff;">Commercial</span></div>
            </div>
          </div>
        </div>
      </div>

      <!-- BOTTOM OVERLAYS -->
      <div style="display:flex; flex-direction:column; align-items:center; gap:24px;">
        
        <!-- Toolbar -->
        <div style="pointer-events:auto; display:flex; align-items:center; gap:8px; background:rgba(12,17,32,0.85); backdrop-filter:blur(14px); border:1px solid rgba(255,255,255,0.1); border-radius:32px; padding:6px 12px; box-shadow:0 8px 32px rgba(0,0,0,0.5);">
          <div style="display:flex; flex-direction:column; align-items:center; gap:4px; padding:6px 12px; cursor:pointer; opacity:0.7; transition:opacity 0.2s;" onmouseover="this.style.opacity=1" onmouseout="this.style.opacity=0.7">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
            <span style="font-size:9px; color:#fff;">Home</span>
          </div>
          <div style="width:1px; height:24px; background:rgba(255,255,255,0.1);"></div>
          <div style="display:flex; flex-direction:column; align-items:center; gap:4px; padding:6px 12px; cursor:pointer; opacity:0.7; transition:opacity 0.2s;" onmouseover="this.style.opacity=1" onmouseout="this.style.opacity=0.7">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>
            <span style="font-size:9px; color:#fff;">Reset View</span>
          </div>
          <div style="width:1px; height:24px; background:rgba(255,255,255,0.1);"></div>
          <div style="display:flex; flex-direction:column; align-items:center; gap:4px; padding:6px 12px; cursor:pointer; opacity:1;">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color:var(--blue);"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="3"/></svg>
            <span style="font-size:9px; color:var(--blue); font-weight:600;">Follow Vehicle</span>
          </div>
          <div style="width:1px; height:24px; background:rgba(255,255,255,0.1);"></div>
          <div style="display:flex; flex-direction:column; align-items:center; gap:4px; padding:6px 12px; cursor:pointer; opacity:0.7; transition:opacity 0.2s;" onmouseover="this.style.opacity=1" onmouseout="this.style.opacity=0.7">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
            <span style="font-size:9px; color:#fff;">Traffic Heatmap</span>
          </div>
          <div style="width:1px; height:24px; background:rgba(255,255,255,0.1);"></div>
          <div style="display:flex; flex-direction:column; align-items:center; gap:4px; padding:6px 12px; cursor:pointer; opacity:0.7; transition:opacity 0.2s;" onmouseover="this.style.opacity=1" onmouseout="this.style.opacity=0.7">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3v18h18"/><path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"/></svg>
            <span style="font-size:9px; color:#fff;">Measure Distance</span>
          </div>
          <div style="width:1px; height:24px; background:rgba(255,255,255,0.1);"></div>
          <div style="display:flex; flex-direction:column; align-items:center; gap:4px; padding:6px 12px; cursor:pointer; opacity:0.7; transition:opacity 0.2s;" onmouseover="this.style.opacity=1" onmouseout="this.style.opacity=0.7">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
            <span style="font-size:9px; color:#fff;">Screenshot</span>
          </div>
        </div>

        <!-- Recent Activity Feed -->
        <div style="pointer-events:auto; width:calc(100% - 360px); align-self:flex-start; background:rgba(12,17,32,0.95); backdrop-filter:blur(14px); border:1px solid rgba(255,255,255,0.07); border-radius:12px; padding:16px; box-shadow:0 8px 32px rgba(0,0,0,0.5); display:flex; flex-direction:column; gap:12px;">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">RECENT ACTIVITY FEED</span>
            <span style="font-size:11px; color:var(--blue); cursor:pointer;">View All &gt;</span>
          </div>
          <div style="display:grid; grid-template-columns:repeat(5, 1fr); gap:12px;">
            <!-- Item 1 -->
            <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.05); border-radius:8px; padding:12px; display:flex; align-items:center; gap:12px;">
              <div style="color:var(--green);"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 17H3a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v5h-3"/><path d="M14 17a2 2 0 1 0 4 0 2 2 0 0 0-4 0"/><path d="M5 17a2 2 0 1 0 4 0 2 2 0 0 0-4 0"/></svg></div>
              <div>
                <div style="font-size:12px; font-weight:700; color:#fff;">TN09AB1234</div>
                <div style="font-size:10px; color:var(--text-muted); margin-top:2px;">Detected at CAM-05</div>
                <div style="font-size:9px; color:var(--text-dim); margin-top:4px;">12:42:18 PM</div>
              </div>
            </div>
            <!-- Item 2 -->
            <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.05); border-radius:8px; padding:12px; display:flex; align-items:center; gap:12px;">
              <div style="color:var(--amber);"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/></svg></div>
              <div>
                <div style="font-size:12px; font-weight:700; color:var(--amber);">Heavy Congestion</div>
                <div style="font-size:10px; color:var(--text-muted); margin-top:2px;">Anna Salai, T. Nagar</div>
                <div style="font-size:9px; color:var(--text-dim); margin-top:4px;">12:41:32 PM</div>
              </div>
            </div>
            <!-- Item 3 -->
            <div style="background:rgba(239,68,68,0.05); border:1px solid rgba(239,68,68,0.2); border-radius:8px; padding:12px; display:flex; align-items:center; gap:12px;">
              <div style="color:var(--red);"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/></svg></div>
              <div>
                <div style="font-size:12px; font-weight:700; color:var(--red);">Accident Detected</div>
                <div style="font-size:10px; color:var(--text-muted); margin-top:2px;">Near Gemini Flyover</div>
                <div style="font-size:9px; color:var(--text-dim); margin-top:4px;">12:40:11 PM</div>
              </div>
            </div>
            <!-- Item 4 -->
            <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.05); border-radius:8px; padding:12px; display:flex; align-items:center; gap:12px;">
              <div style="color:var(--blue);"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 17H3a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v5h-3"/><path d="M14 17a2 2 0 1 0 4 0 2 2 0 0 0-4 0"/><path d="M5 17a2 2 0 1 0 4 0 2 2 0 0 0-4 0"/></svg></div>
              <div>
                <div style="font-size:12px; font-weight:700; color:#fff;">TN07CD5678</div>
                <div style="font-size:10px; color:var(--text-muted); margin-top:2px;">Detected at CAM-11</div>
                <div style="font-size:9px; color:var(--text-dim); margin-top:4px;">12:39:47 PM</div>
              </div>
            </div>
            <!-- Item 5 -->
            <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.05); border-radius:8px; padding:12px; display:flex; align-items:center; gap:12px;">
              <div style="color:var(--blue);"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg></div>
              <div>
                <div style="font-size:12px; font-weight:700; color:#fff;">CAM-12</div>
                <div style="font-size:10px; color:var(--text-muted); margin-top:2px;">Back Online</div>
                <div style="font-size:9px; color:var(--text-dim); margin-top:4px;">12:38:55 PM</div>
              </div>
            </div>
          </div>
        </div>

      </div>

    </div>
  `;
}

// Keeping this to prevent crashes when other files try to import it.
// Real event wiring can happen here later.
// Real event wiring can happen here later.
export async function initMapOverlayEvents(viewer, layerManager) {
  try {
    const backendUrl = (import.meta.env.VITE_BACKEND_URL || '').replace(/\/$/, '');
    const response = await fetch(`${backendUrl}/api/v1/cameras/sessions`);
    if (response.ok) {
      const sessions = await response.json();
      let centered = false;
      sessions.forEach(session => {
        if (session.latitude && session.longitude) {
          viewer.entities.add({
            id: `cam-${session.session_id}`,
            position: Cesium.Cartesian3.fromDegrees(session.longitude, session.latitude, 50), // 50m above ground
            billboard: {
              image: 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSIjM2I4MmY2IiBzdHJva2U9IiNmZmYiIHN0cm9rZS13aWR0aD0iMiI+PHBhdGggZD0iTTIzIDE5YTIgMiAwIDAgMS0yIDJIMUMzYTIgMiAwIDAgMSAxIDE5VjhhMiAyIDAgMCAxIDItMmg0bDItM2g2bDIgM2g0YTIgMiAwIDAgMSAyIDJ6Ii8+PGNpcmNsZSBjeD0iMTIiIGN5PSIxMyIgcj0iNCIvPjwvc3ZnPg==',
              scale: 1.5,
              verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
            },
            label: {
              text: `CAM-${session.session_id.substring(0, 4).toUpperCase()} (LIVE)`,
              font: 'bold 12pt sans-serif',
              style: Cesium.LabelStyle.FILL_AND_OUTLINE,
              fillColor: Cesium.Color.WHITE,
              outlineColor: Cesium.Color.BLACK,
              outlineWidth: 2,
              verticalOrigin: Cesium.VerticalOrigin.TOP,
              pixelOffset: new Cesium.Cartesian2(0, 10),
            }
          });
          
          if (!centered) {
            viewer.camera.flyTo({
              destination: Cesium.Cartesian3.fromDegrees(session.longitude, session.latitude, 2000),
              orientation: {
                heading: Cesium.Math.toRadians(0.0),
                pitch: Cesium.Math.toRadians(-45.0),
                roll: 0.0
              },
              duration: 2.0
            });
            centered = true;
          }
        }
      });
    }
  } catch(e) {
    console.error("Failed to fetch cameras for map", e);
  }
}
