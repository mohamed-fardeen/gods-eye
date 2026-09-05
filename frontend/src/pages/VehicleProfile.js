export function renderVehicleProfile() {
  return `
    <div style="padding: 24px; display: flex; flex-direction: column; gap: 20px; flex: 1; overflow-y: auto;">
      
      <!-- Top Row: Headers & Summaries -->
      <div style="display: flex; gap: 20px;">
        
        <!-- Left: Vehicle Info Panel -->
        <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 20px; width: 380px; flex-shrink: 0; display: flex; flex-direction: column; gap: 16px;">
          <div style="display: flex; align-items: center; gap: 8px; color: var(--blue); font-size: 11px; font-weight: 600; cursor: pointer;">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
            Back to Search
          </div>
          
          <div style="display: flex; align-items: center; gap: 12px;">
            <div style="font-size: 24px; font-weight: 800; color: #fff; letter-spacing: 1px;">TN09AB1234</div>
            <div style="background: rgba(34,197,94,0.1); border: 1px solid rgba(34,197,94,0.3); color: var(--green); font-size: 9px; font-weight: 700; padding: 4px 8px; border-radius: 4px; text-transform: uppercase; letter-spacing: 0.5px;">Tracked</div>
          </div>
          
          <div style="display: flex; gap: 20px; margin-top: 8px;">
            <!-- Vehicle Image Box -->
            <div style="width: 140px; height: 105px; background: rgba(0,0,0,0.5); border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);"></div>
            
            <div style="flex: 1; display: flex; flex-direction: column; gap: 6px; font-size: 11px;">
              <div style="display:flex; justify-content:space-between;"><span style="color:var(--text-dim);">Vehicle Type</span><span style="color:#fff; font-weight:600;">Sedan</span></div>
              <div style="display:flex; justify-content:space-between;"><span style="color:var(--text-dim);">Vehicle Color</span><span style="color:#fff; font-weight:600;">White</span></div>
              <div style="display:flex; justify-content:space-between;"><span style="color:var(--text-dim);">Make</span><span style="color:#fff; font-weight:600;">Honda</span></div>
              <div style="display:flex; justify-content:space-between;"><span style="color:var(--text-dim);">Model</span><span style="color:#fff; font-weight:600;">City</span></div>
              <div style="display:flex; justify-content:space-between;"><span style="color:var(--text-dim);">Year</span><span style="color:#fff; font-weight:600;">2019</span></div>
              <div style="display:flex; justify-content:space-between;"><span style="color:var(--text-dim);">Confidence</span><span style="color:#fff; font-weight:600;">96%</span></div>
            </div>
          </div>
        </div>

        <!-- Right: 4 Statistic Cards -->
        <div style="flex: 1; display: flex; gap: 20px;">
          
          <!-- First Seen -->
          <div style="flex: 1; background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 20px; display: flex; flex-direction: column; justify-content: space-between;">
            <div style="font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px;">FIRST SEEN</div>
            <div style="display: flex; flex-direction: column; gap: 4px;">
              <div style="display: flex; align-items: center; gap: 8px; color: var(--blue);">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                <span style="font-size: 13px; font-weight: 700; color: #fff;">21 May 2024</span>
              </div>
              <div style="font-size: 13px; font-weight: 700; color: #fff; padding-left: 28px;">10:32:18 AM</div>
            </div>
            <div style="font-size: 11px; color: var(--text-200); line-height: 1.6;">
              <div style="color: var(--text-muted);">CAM-03</div>
              <div>Anna Salai Junction</div>
            </div>
          </div>

          <!-- Last Seen -->
          <div style="flex: 1; background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 20px; display: flex; flex-direction: column; justify-content: space-between;">
            <div style="font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px;">LAST SEEN</div>
            <div style="display: flex; flex-direction: column; gap: 4px;">
              <div style="display: flex; align-items: center; gap: 8px; color: var(--blue);">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                <span style="font-size: 13px; font-weight: 700; color: #fff;">21 May 2024</span>
              </div>
              <div style="font-size: 13px; font-weight: 700; color: #fff; padding-left: 28px;">12:43:52 PM</div>
            </div>
            <div style="font-size: 11px; color: var(--text-200); line-height: 1.6;">
              <div style="color: var(--text-muted);">CAM-21</div>
              <div>Besant Nagar Beach Rd</div>
            </div>
          </div>

          <!-- Total Detections -->
          <div style="flex: 1; background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 20px; display: flex; flex-direction: column; justify-content: space-between;">
            <div style="font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px;">TOTAL DETECTIONS</div>
            <div style="display: flex; flex-direction: column; gap: 4px;">
              <div style="display: flex; align-items: center; gap: 8px; color: var(--blue);">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>
                <span style="font-size: 24px; font-weight: 800; color: #fff;">17</span>
              </div>
            </div>
            <div style="font-size: 11px; color: var(--text-200);">Across 7 Cameras</div>
            <button style="margin-top: 8px; width: 100%; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; padding: 8px; color: var(--blue); font-size: 11px; font-weight: 600; cursor: pointer;">View All Detections</button>
          </div>

          <!-- Current Status -->
          <div style="flex: 1.5; background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 20px; display: flex; flex-direction: column; justify-content: space-between;">
            <div style="font-size: 11px; font-weight: 700; color: var(--green); text-transform: uppercase; letter-spacing: 0.5px;">CURRENT STATUS</div>
            <div style="font-size: 12px; color: #fff; font-weight: 600;">Last Seen: 12:43:52 PM</div>
            <div style="display: flex; flex-direction: column; gap: 6px; font-size: 11px;">
              <div style="display:flex;"><span style="width:70px; color:var(--text-dim);">Location</span><span style="color:var(--text-200);">Besant Nagar Beach Rd</span></div>
              <div style="display:flex;"><span style="width:70px; color:var(--text-dim);">Speed</span><span style="color:var(--text-200);">42 km/h</span></div>
              <div style="display:flex;"><span style="width:70px; color:var(--text-dim);">Direction</span><span style="color:var(--text-200);">South</span></div>
            </div>
            <button style="margin-top: 8px; width: 100%; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; padding: 8px; color: var(--blue); font-size: 11px; font-weight: 600; cursor: pointer;">View on Map</button>
          </div>

        </div>
      </div>

      <!-- Middle Row: Map and List -->
      <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 20px; flex-shrink: 0; min-height: 400px;">
        
        <!-- Left: Map -->
        <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; display: flex; flex-direction: column; overflow: hidden; position: relative;">
          <div style="padding: 16px 20px; border-bottom: 1px solid rgba(255,255,255,0.05); background: rgba(0,0,0,0.2); position:absolute; top:0; left:0; right:0; z-index:10; pointer-events:none;">
            <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px; pointer-events:auto;">MOVEMENT PATH</span>
          </div>
          
          <div id="vehicleprofile-map" style="flex: 1; min-height: 0; background: #000; position: relative; z-index: 1;">
            <!-- Leaflet map goes here -->
          </div>

          <!-- Map Legend -->
          <div style="position: absolute; bottom: 16px; left: 16px; background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 8px; padding: 8px 12px; display: flex; gap: 16px; align-items: center; z-index: 1000;">
            <div style="display:flex; align-items:center; gap:6px;"><div style="width:8px; height:8px; border-radius:50%; background:var(--green);"></div><span style="font-size:10px; color:var(--text-200);">Entry</span></div>
            <div style="display:flex; align-items:center; gap:6px;"><div style="width:8px; height:8px; border-radius:50%; background:var(--amber);"></div><span style="font-size:10px; color:var(--text-200);">Moving</span></div>
            <div style="display:flex; align-items:center; gap:6px;"><div style="width:8px; height:8px; border-radius:50%; background:var(--red);"></div><span style="font-size:10px; color:var(--text-200);">Exit</span></div>
          </div>
          
          <!-- Zoom Controls placeholder (in addition to leaflet's) -->
          <div style="position: absolute; top: 16px; right: 16px; display:flex; flex-direction:column; gap:8px; z-index: 1000;">
            <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; display:flex; flex-direction:column;">
              <div style="padding:6px; border-bottom:1px solid rgba(255,255,255,0.1); cursor:pointer; display:flex; justify-content:center; color:#fff;"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg></div>
              <div style="padding:6px; cursor:pointer; display:flex; justify-content:center; color:#fff;"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="5" y1="12" x2="19" y2="12"/></svg></div>
            </div>
            <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; padding:6px; cursor:pointer; display:flex; justify-content:center; color:#fff;"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="3"/></svg></div>
          </div>
        </div>

        <!-- Right: Detection History List -->
        <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; display: flex; flex-direction: column; overflow: hidden;">
          <div style="padding: 16px 20px; border-bottom: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-between; align-items: center; background: rgba(0,0,0,0.2);">
            <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">DETECTION HISTORY (All)</span>
            <span style="font-size:10px; color:var(--blue); cursor:pointer;">View All</span>
          </div>
          
          <div style="flex: 1; overflow-y: auto; padding: 12px 20px; display: flex; flex-direction: column; gap: 16px; position:relative;">
            <!-- Timeline line -->
            <div style="position:absolute; left:32px; top:20px; bottom:20px; width:2px; background:rgba(255,255,255,0.05); z-index:1;"></div>
            
            ${renderHistoryItem(1, 'var(--green)', 'CAM-03', 'Anna Salai Junction', '21 May 2024', '10:32:18 AM', 'Entry', 'var(--green)')}
            ${renderHistoryItem(2, '#4ade80', 'CAM-05', 'T. Nagar Signal', '21 May 2024', '10:41:07 AM', 'Moving', 'var(--blue)')}
            ${renderHistoryItem(3, '#65a30d', 'CAM-07', 'Guindy Signal', '21 May 2024', '11:02:33 AM', 'Moving', 'var(--blue)')}
            ${renderHistoryItem(4, '#84cc16', 'CAM-11', 'Adyar Bridge', '21 May 2024', '11:37:21 AM', 'Moving', 'var(--blue)')}
            ${renderHistoryItem(5, '#a3e635', 'CAM-15', 'Thiruvanmiyur Junction', '21 May 2024', '12:05:44 PM', 'Moving', 'var(--blue)')}
            ${renderHistoryItem(6, '#d9f99d', 'CAM-18', 'ECR Road Junction', '21 May 2024', '12:26:10 PM', 'Moving', 'var(--blue)')}
            ${renderHistoryItem(7, 'var(--red)', 'CAM-21', 'Besant Nagar Beach Rd', '21 May 2024', '12:43:52 PM', 'Exit', 'var(--red)', true)}
          </div>
        </div>

      </div>

      <!-- Bottom Row: Timeline & Summary -->
      <div style="display: grid; grid-template-columns: 2fr 1fr 1.5fr; gap: 20px; flex-shrink: 0;">
        
        <!-- Timeline -->
        <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 16px 20px; overflow-x: auto;">
          <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px; margin-bottom: 24px; display:block;">TIMELINE</span>
          
          <div style="display: flex; justify-content: space-between; align-items: flex-start; position: relative; padding-top: 10px;">
            <!-- Horizontal Line -->
            <div style="position: absolute; left: 20px; right: 20px; top: 22px; height: 2px; background: linear-gradient(90deg, var(--green), #84cc16, var(--orange), var(--red)); z-index: 1;"></div>
            
            ${renderHorizontalTimelineItem(1, 'var(--green)', '10:32 AM', 'CAM-03', 'Anna Salai Junction')}
            ${renderHorizontalTimelineItem(2, '#4ade80', '10:41 AM', 'CAM-05', 'T. Nagar Signal')}
            ${renderHorizontalTimelineItem(3, '#65a30d', '11:02 AM', 'CAM-07', 'Guindy Signal')}
            ${renderHorizontalTimelineItem(4, '#84cc16', '11:37 AM', 'CAM-11', 'Adyar Bridge')}
            ${renderHorizontalTimelineItem(5, '#a3e635', '12:05 PM', 'CAM-15', 'Thiruvanmiyur Junction')}
            ${renderHorizontalTimelineItem(6, '#d9f99d', '12:26 PM', 'CAM-18', 'ECR Road Junction')}
            ${renderHorizontalTimelineItem(7, 'var(--red)', '12:43 PM', 'CAM-21', 'Besant Nagar Beach Rd')}
          </div>
        </div>

        <!-- Path Summary -->
        <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 16px 20px;">
          <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px; margin-bottom: 20px; display:block;">PATH SUMMARY</span>
          
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: y-16px; row-gap: 20px;">
            <div>
              <div style="font-size: 9px; color: var(--text-dim); text-transform: uppercase;">TOTAL DISTANCE</div>
              <div style="display:flex; align-items:center; gap:6px; color:var(--green); margin-top:4px;">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s-8-4.5-8-11.8A8 8 0 0 1 12 2a8 8 0 0 1 8 8.2c0 7.3-8 11.8-8 11.8z"/><circle cx="12" cy="10" r="3"/></svg>
                <span style="font-size: 15px; font-weight: 700; color: #fff;">28.6 <span style="font-size:11px; font-weight:400; color:var(--text-muted);">km</span></span>
              </div>
            </div>
            <div>
              <div style="font-size: 9px; color: var(--text-dim); text-transform: uppercase;">TOTAL TIME</div>
              <div style="display:flex; align-items:center; gap:6px; color:var(--blue); margin-top:4px;">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                <span style="font-size: 15px; font-weight: 700; color: #fff;">2h 11m <span style="font-size:11px; font-weight:400; color:var(--text-muted);">34s</span></span>
              </div>
            </div>
            <div>
              <div style="font-size: 9px; color: var(--text-dim); text-transform: uppercase;">AVG SPEED</div>
              <div style="display:flex; align-items:center; gap:6px; color:var(--blue); margin-top:4px;">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
                <span style="font-size: 13px; font-weight: 700; color: #fff;">23.4 <span style="font-size:11px; font-weight:400; color:var(--text-muted);">km/h</span></span>
              </div>
            </div>
            <div>
              <div style="font-size: 9px; color: var(--text-dim); text-transform: uppercase;">MAX SPEED</div>
              <div style="display:flex; align-items:center; gap:6px; color:var(--red); margin-top:4px;">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
                <span style="font-size: 13px; font-weight: 700; color: #fff;">56 <span style="font-size:11px; font-weight:400; color:var(--text-muted);">km/h</span></span>
              </div>
            </div>
          </div>
        </div>

        <!-- Vehicle Snapshots -->
        <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 16px 20px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">VEHICLE SNAPSHOTS</span>
            <span style="font-size:10px; color:var(--blue); cursor:pointer;">View All</span>
          </div>
          <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px;">
            <div style="display:flex; flex-direction:column; gap:6px; align-items:center;">
              <div style="width:100%; aspect-ratio:4/3; background:rgba(0,0,0,0.5); border:1px solid rgba(255,255,255,0.1); border-radius:6px;"></div>
              <div style="font-size:9px; color:var(--text-200); text-align:center;">10:32:18 AM<br><span style="color:var(--text-muted);">CAM-03</span></div>
            </div>
            <div style="display:flex; flex-direction:column; gap:6px; align-items:center;">
              <div style="width:100%; aspect-ratio:4/3; background:rgba(0,0,0,0.5); border:1px solid rgba(255,255,255,0.1); border-radius:6px;"></div>
              <div style="font-size:9px; color:var(--text-200); text-align:center;">11:02:33 AM<br><span style="color:var(--text-muted);">CAM-07</span></div>
            </div>
            <div style="display:flex; flex-direction:column; gap:6px; align-items:center;">
              <div style="width:100%; aspect-ratio:4/3; background:rgba(0,0,0,0.5); border:1px solid rgba(255,255,255,0.1); border-radius:6px;"></div>
              <div style="font-size:9px; color:var(--text-200); text-align:center;">11:37:21 AM<br><span style="color:var(--text-muted);">CAM-11</span></div>
            </div>
            <div style="display:flex; flex-direction:column; gap:6px; align-items:center;">
              <div style="width:100%; aspect-ratio:4/3; background:rgba(0,0,0,0.5); border:1px solid rgba(255,255,255,0.1); border-radius:6px;"></div>
              <div style="font-size:9px; color:var(--text-200); text-align:center;">12:43:52 PM<br><span style="color:var(--text-muted);">CAM-21</span></div>
            </div>
          </div>
        </div>

      </div>

      <!-- Footer Info -->
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <div style="display:flex; align-items:center; gap:6px; color:var(--blue); font-size:11px;">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
          <span style="color:var(--text-muted);">Note: All times are in IST (UTC +5:30). Data is updated in real-time.</span>
        </div>
        <button style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 8px 16px; color: var(--text-200); font-size: 12px; display: flex; align-items: center; gap: 8px; cursor: pointer;">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg> Export Report
        </button>
      </div>

    </div>
  `;
}

function renderHistoryItem(num, bgColor, camId, loc, date, time, status, statusColor, isLast=false) {
  return `
    <div style="display: flex; gap: 12px; position: relative; z-index: 2;">
      <div style="width: 24px; height: 24px; border-radius: 50%; background: ${bgColor}; color: ${num===1||num===7 ? '#fff' : '#000'}; font-size: 11px; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 0 0 4px rgba(12,17,32,1);">${num}</div>
      <div style="flex: 1; display: flex; gap: 12px; padding-bottom: ${isLast ? '0' : '16px'};">
        <div style="width: 48px; height: 36px; background: rgba(0,0,0,0.5); border-radius: 4px; border: 1px solid rgba(255,255,255,0.1); flex-shrink: 0;"></div>
        <div style="flex: 1; display: flex; justify-content: space-between; align-items: flex-start;">
          <div style="display:flex; flex-direction:column; gap:2px;">
            <div style="font-size: 11px; color: var(--text-200);"><span style="font-weight:600; color:#fff;">${camId}</span> ${loc}</div>
            <div style="font-size: 10px; color: var(--text-dim);">${date} <span style="margin-left:4px;">${time}</span></div>
          </div>
          <div style="background: transparent; border: 1px solid rgba(${statusColor === 'var(--green)' ? '34,197,94' : statusColor === 'var(--red)' ? '239,68,68' : '59,130,246'}, 0.3); color: ${statusColor}; font-size: 9px; font-weight: 600; padding: 2px 8px; border-radius: 4px;">${status}</div>
        </div>
      </div>
    </div>
  `;
}

function renderHorizontalTimelineItem(num, bgColor, time, camId, loc) {
  return `
    <div style="display: flex; flex-direction: column; align-items: center; gap: 8px; width: 60px; position: relative; z-index: 2;">
      <div style="width: 24px; height: 24px; border-radius: 50%; background: ${bgColor}; color: ${num===1||num===7 ? '#fff' : '#000'}; font-size: 11px; font-weight: 700; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 0 4px rgba(12,17,32,1);">${num}</div>
      
      <div style="display:flex; flex-direction:column; align-items:center; text-align:center;">
        <div style="font-size: 10px; font-weight: 600; color: #fff;">${time}</div>
        <div style="font-size: 9px; font-weight: 700; color: var(--text-200); margin-top:2px;">${camId}</div>
        <div style="font-size: 8px; color: var(--text-dim); line-height: 1.2; overflow:hidden; text-overflow:ellipsis; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical;">${loc}</div>
      </div>
      
      <div style="width: 48px; height: 36px; background: rgba(0,0,0,0.5); border-radius: 4px; border: 1px solid rgba(255,255,255,0.1); margin-top: 4px;"></div>
    </div>
  `;
}

export function initVehicleProfileMap() {
  const mapContainer = document.getElementById('vehicleprofile-map');
  if (!mapContainer || mapContainer._leaflet_id) return;
  
  const map = L.map('vehicleprofile-map', {
    zoomControl: false,
    attributionControl: false
  }).setView([13.02, 80.24], 12);
  
  // Use standard OpenStreetMap tiles with dark CSS filter
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    className: 'dark-map-tiles'
  }).addTo(map);

  // Draw movement path (Timeline 1 to 7)
  const pathCoordinates = [
    [13.06, 80.25], // 1: Anna Salai
    [13.04, 80.24], // 2: T. Nagar
    [13.02, 80.22], // 3: Guindy
    [13.00, 80.25], // 4: Adyar Bridge
    [12.98, 80.26], // 5: Thiruvanmiyur
    [12.96, 80.25], // 6: ECR
    [12.99, 80.27]  // 7: Besant Nagar
  ];
  
  L.polyline(pathCoordinates, { color: '#f59e0b', weight: 3, dashArray: '6, 6' }).addTo(map);
  
  // Add markers with numbers
  const colors = [
    'var(--green)', '#4ade80', '#65a30d', '#84cc16', '#a3e635', '#d9f99d', 'var(--red)'
  ];
  
  pathCoordinates.forEach((coord, i) => {
    const isFirst = i === 0;
    const isLast = i === pathCoordinates.length - 1;
    
    let html = `<div style="width:16px; height:16px; border-radius:50%; background:${colors[i]}; border: 2px solid #000; box-shadow: 0 0 4px rgba(0,0,0,0.5);"></div>`;
    
    // Add ping effect to the last point
    if (isLast) {
      html += `<div style="position:absolute; top:-2px; left:-2px; width:20px; height:20px; border-radius:50%; border: 2px solid var(--red); animation: ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite;"></div>`;
    }

    // Add labels next to markers for 1, 3, 5, 7 just to populate the map a bit
    if (i % 2 === 0) {
        const camLabels = ['CAM-03<br/>10:32 AM', '', 'CAM-07<br/>11:02 AM', '', 'CAM-15<br/>12:05 PM', '', 'CAM-21<br/>12:43 PM'];
        html += `<div style="position:absolute; top:-4px; left:22px; width:60px; font-size:9px; color:#fff; font-weight:600; text-shadow: 1px 1px 2px #000;">${camLabels[i]}</div>`;
    }

    const icon = L.divIcon({
      html,
      className: '',
      iconSize: [16, 16],
      iconAnchor: [8, 8]
    });
    L.marker(coord, { icon }).addTo(map);
  });
}
