export function renderDashboard() {
  return `
    <div style="padding: 12px 16px; display: flex; flex-direction: column; gap: 12px; height: 100%; overflow-y: auto;">
      
      <!-- TOP ROW: KPIs -->
      <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px;">
        <!-- KPI 1 -->
        <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 12px 16px; display: flex; align-items: center; gap: 12px;">
          <div style="color:var(--blue);"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 17H3a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v5h-3"/><path d="M14 17a2 2 0 1 0 4 0 2 2 0 0 0-4 0"/><path d="M5 17a2 2 0 1 0 4 0 2 2 0 0 0-4 0"/></svg></div>
          <div>
            <div style="font-size:10px; color:var(--text-muted); text-transform:uppercase; font-weight:700;">TOTAL VEHICLES</div>
            <div style="display:flex; align-items:baseline; gap:6px;">
              <div style="font-size:20px; font-weight:800; color:#fff;">1,284</div>
              <div style="font-size:11px; color:var(--green);"><svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" style="display:inline; margin-right:2px;"><polyline points="18 15 12 9 6 15"/></svg>12.5%</div>
            </div>
            <div style="font-size:9px; color:var(--text-dim); margin-top:-2px;">vs yesterday</div>
          </div>
        </div>
        
        <!-- KPI 2 -->
        <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(34,197,94,0.3); border-radius: 12px; padding: 12px 16px; display: flex; align-items: center; gap: 12px; box-shadow: 0 0 15px rgba(34,197,94,0.05);">
          <div style="color:var(--green);"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg></div>
          <div>
            <div style="font-size:10px; color:var(--green); text-transform:uppercase; font-weight:700;">ACTIVE CAMERAS</div>
            <div style="display:flex; align-items:baseline; gap:4px;">
              <div style="font-size:20px; font-weight:800; color:#fff;">42</div>
              <div style="font-size:14px; color:var(--text-muted);">/ 48</div>
            </div>
            <div style="font-size:9px; color:var(--text-dim); margin-top:-2px;">Online</div>
          </div>
        </div>

        <!-- KPI 3 -->
        <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(239,68,68,0.3); border-radius: 12px; padding: 12px 16px; display: flex; align-items: center; gap: 12px; box-shadow: 0 0 15px rgba(239,68,68,0.05);">
          <div style="color:var(--red);"><svg width="28" height="28" viewBox="0 0 24 24" fill="var(--red-dim)" stroke="currentColor" stroke-width="2"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg></div>
          <div>
            <div style="font-size:10px; color:var(--red); text-transform:uppercase; font-weight:700;">ACTIVE ALERTS</div>
            <div style="font-size:20px; font-weight:800; color:#fff;">7</div>
            <div style="font-size:9px; color:var(--text-dim); margin-top:-2px;">High Priority</div>
          </div>
        </div>

        <!-- KPI 4 -->
        <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(245,158,11,0.3); border-radius: 12px; padding: 12px 16px; display: flex; align-items: center; gap: 12px; box-shadow: 0 0 15px rgba(245,158,11,0.05);">
          <div style="color:var(--amber);"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="7" y="2" width="10" height="20" rx="3"/><circle cx="12" cy="7" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="12" cy="17" r="2"/></svg></div>
          <div>
            <div style="font-size:10px; color:var(--amber); text-transform:uppercase; font-weight:700;">TRAFFIC STATUS</div>
            <div style="font-size:20px; font-weight:800; color:var(--amber);">HIGH</div>
            <div style="font-size:9px; color:var(--text-dim); margin-top:-2px;">Congestion Level</div>
          </div>
        </div>

        <!-- KPI 5 -->
        <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 12px 16px; display: flex; align-items: center; gap: 12px;">
          <div style="color:var(--purple);"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg></div>
          <div>
            <div style="font-size:10px; color:var(--text-muted); text-transform:uppercase; font-weight:700;">PEOPLE ON ROADS</div>
            <div style="font-size:20px; font-weight:800; color:#fff;">18,560</div>
            <div style="font-size:9px; color:var(--text-dim); margin-top:-2px;">Estimated</div>
          </div>
        </div>
      </div>

      <!-- MIDDLE ROW -->
      <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 12px; flex: 1; min-height: 0; flex: 1.5;">
        
        <!-- Live City Overview (Map) -->
        <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; display: flex; flex-direction: column; overflow: hidden; position: relative; z-index: 1;">
          <div style="padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.07); display: flex; justify-content: space-between; align-items: center; flex-shrink: 0; position:relative; z-index:10; background: rgba(12,17,32,0.9);">
            <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">LIVE CITY OVERVIEW</span>
          </div>
          <!-- Apply min-height: 0 so flex: 1 doesn't overflow -->
          <div id="leaflet-map" style="flex: 1; min-height: 0; background: #000; position: relative; z-index: 1;">
            <!-- Leaflet map goes here -->
          </div>
          <!-- Legend Overlay -->
          <div style="position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 20px; padding: 8px 16px; display: flex; gap: 12px; align-items: center; z-index: 1000; box-shadow: 0 4px 12px rgba(0,0,0,0.5);">
            <div style="display:flex; align-items:center; gap:8px;"><div style="width:16px; height:3px; background:var(--green); border-radius:2px;"></div><span style="font-size:10px; color:var(--text-200);">Smooth</span></div>
            <div style="display:flex; align-items:center; gap:8px;"><div style="width:16px; height:3px; background:var(--amber); border-radius:2px;"></div><span style="font-size:10px; color:var(--text-200);">Moderate</span></div>
            <div style="display:flex; align-items:center; gap:8px;"><div style="width:16px; height:3px; background:#f97316; border-radius:2px;"></div><span style="font-size:10px; color:var(--text-200);">Heavy</span></div>
            <div style="display:flex; align-items:center; gap:8px;"><div style="width:16px; height:3px; background:var(--red); border-radius:2px;"></div><span style="font-size:10px; color:var(--text-200);">Severe</span></div>
            <div style="display:flex; align-items:center; gap:8px;"><div style="width:16px; height:3px; background:var(--text-muted); border-radius:2px;"></div><span style="font-size:10px; color:var(--text-200);">No Data</span></div>
          </div>
        </div>

        <!-- Right Panels -->
        <div style="display: flex; flex-direction: column; gap: 12px;">
          
          <!-- Recent Alerts -->
          <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; display: flex; flex-direction: column; flex: 1; overflow: hidden;">
            <div style="padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.07); display: flex; justify-content: space-between; align-items: center;">
              <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">RECENT ALERTS</span>
              <span style="font-size:10px; color:var(--blue); cursor:pointer;">View All</span>
            </div>
            <div style="padding: 8px 0; overflow-y: auto;">
              <!-- Alert Item 1 -->
              <div style="display:flex; gap:12px; padding:12px 20px; border-bottom:1px solid rgba(255,255,255,0.03);">
                <div style="color:var(--red); margin-top:2px;"><svg width="20" height="20" viewBox="0 0 24 24" fill="var(--red-dim)" stroke="currentColor" stroke-width="2"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg></div>
                <div style="flex:1;">
                  <div style="font-size:12px; font-weight:600; color:var(--text-100);">Accident Detected</div>
                  <div style="font-size:10px; color:var(--text-muted); margin-top:2px;">Anna Salai, Near Gemini Flyover</div>
                </div>
                <div style="font-size:10px; color:var(--text-dim);">12:43 PM</div>
              </div>
              <!-- Alert Item 2 -->
              <div style="display:flex; gap:12px; padding:12px 20px; border-bottom:1px solid rgba(255,255,255,0.03);">
                <div style="color:var(--red); margin-top:2px;"><svg width="20" height="20" viewBox="0 0 24 24" fill="var(--red-dim)" stroke="currentColor" stroke-width="2"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg></div>
                <div style="flex:1;">
                  <div style="font-size:12px; font-weight:600; color:var(--text-100);">Wrong Way Vehicle</div>
                  <div style="font-size:10px; color:var(--text-muted); margin-top:2px;">OMR, Near Perungudi</div>
                </div>
                <div style="font-size:10px; color:var(--text-dim);">12:38 PM</div>
              </div>
              <!-- Alert Item 3 -->
              <div style="display:flex; gap:12px; padding:12px 20px; border-bottom:1px solid rgba(255,255,255,0.03);">
                <div style="color:var(--amber); margin-top:2px;"><svg width="20" height="20" viewBox="0 0 24 24" fill="var(--amber-dim)" stroke="currentColor" stroke-width="2"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg></div>
                <div style="flex:1;">
                  <div style="font-size:12px; font-weight:600; color:var(--text-100);">Heavy Congestion</div>
                  <div style="font-size:10px; color:var(--text-muted); margin-top:2px;">Mount Road, T. Nagar</div>
                </div>
                <div style="font-size:10px; color:var(--text-dim);">12:32 PM</div>
              </div>
              <!-- Alert Item 4 -->
              <div style="display:flex; gap:12px; padding:12px 20px;">
                <div style="color:var(--amber); margin-top:2px;"><svg width="20" height="20" viewBox="0 0 24 24" fill="var(--amber-dim)" stroke="currentColor" stroke-width="2"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg></div>
                <div style="flex:1;">
                  <div style="font-size:12px; font-weight:600; color:var(--text-100);">Signal Violation</div>
                  <div style="font-size:10px; color:var(--text-muted); margin-top:2px;">Velachery, 100ft Road</div>
                </div>
                <div style="font-size:10px; color:var(--text-dim);">12:28 PM</div>
              </div>
            </div>
          </div>

          <!-- Traffic Summary -->
          <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; display: flex; flex-direction: column; overflow: hidden; min-height: 0; flex: 1; flex-shrink: 0;">
            <div style="padding: 14px 20px; display: flex; justify-content: space-between; align-items: center;">
              <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">TRAFFIC SUMMARY</span>
              <span style="font-size:10px; color:var(--blue); cursor:pointer;">View Details</span>
            </div>
            <div style="display:flex; align-items:center; padding: 0 20px; gap:20px;">
              <!-- Donut Chart -->
              <div style="width:110px; height:110px; position:relative; display:flex; align-items:center; justify-content:center;">
                <svg viewBox="0 0 36 36" style="width:100%; height:100%;">
                  <!-- Background ring -->
                  <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="4"/>
                  <!-- Segments (CSS will animate stroke-dasharray) -->
                  <path class="donut-segment" stroke="var(--blue)" stroke-width="4" stroke-dasharray="65 35" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none"/>
                  <path class="donut-segment" stroke="var(--green)" stroke-width="4" stroke-dasharray="24 76" stroke-dashoffset="-65" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none"/>
                  <path class="donut-segment" stroke="#f97316" stroke-width="4" stroke-dasharray="7 93" stroke-dashoffset="-89" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none"/>
                  <path class="donut-segment" stroke="#eab308" stroke-width="4" stroke-dasharray="4 96" stroke-dashoffset="-96" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none"/>
                </svg>
                <div style="position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center;">
                  <div style="font-size:9px; color:var(--text-muted); font-weight:700;">TOTAL</div>
                  <div style="font-size:16px; font-weight:800; color:#fff;">1,284</div>
                </div>
              </div>
              <!-- Legend -->
              <div style="flex:1; display:flex; flex-direction:column; gap:6px;">
                <div style="display:flex; justify-content:space-between; align-items:center; font-size:11px;">
                  <div style="display:flex; align-items:center; gap:6px;"><div style="width:8px; height:8px; border-radius:50%; background:var(--blue);"></div><span style="color:var(--text-200);">Cars</span></div>
                  <div style="color:#fff;">842 <span style="color:var(--text-muted); font-size:10px;">(65%)</span></div>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; font-size:11px;">
                  <div style="display:flex; align-items:center; gap:6px;"><div style="width:8px; height:8px; border-radius:50%; background:var(--green);"></div><span style="color:var(--text-200);">Two Wheelers</span></div>
                  <div style="color:#fff;">623 <span style="color:var(--text-muted); font-size:10px;">(24%)</span></div>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; font-size:11px;">
                  <div style="display:flex; align-items:center; gap:6px;"><div style="width:8px; height:8px; border-radius:50%; background:#f97316;"></div><span style="color:var(--text-200);">Buses</span></div>
                  <div style="color:#fff;">87 <span style="color:var(--text-muted); font-size:10px;">(7%)</span></div>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; font-size:11px;">
                  <div style="display:flex; align-items:center; gap:6px;"><div style="width:8px; height:8px; border-radius:50%; background:#eab308;"></div><span style="color:var(--text-200);">Trucks</span></div>
                  <div style="color:#fff;">54 <span style="color:var(--text-muted); font-size:10px;">(4%)</span></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- BOTTOM ROW -->
      <div style="display: grid; grid-template-columns: 1.2fr 1.3fr 1.5fr; gap: 12px; min-height: 0; flex: 1;">
        
        <!-- Peak Hours -->
        <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 12px 16px; display: flex; flex-direction: column;">
          <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px; margin-bottom: 20px;">PEAK HOURS TODAY</span>
          <!-- Chart -->
          <div style="flex:1; display:flex; align-items:flex-end; gap:6px; position:relative;">
            <!-- Tooltip -->
            <div style="position:absolute; top:-10px; right:20px; background:#1e293b; border:1px solid rgba(255,255,255,0.1); border-radius:6px; padding:6px 10px; display:flex; flex-direction:column; align-items:center;">
              <span style="font-size:9px; color:var(--text-muted);">6 PM - 7 PM</span>
              <span style="font-size:11px; font-weight:600; color:#fff;">1,856 Vehicles</span>
            </div>
            
            <!-- Bars -->
            <div style="flex:1; height:15%; background:var(--blue); border-radius:2px; opacity:0.5;"></div>
            <div style="flex:1; height:20%; background:var(--blue); border-radius:2px; opacity:0.5;"></div>
            <div style="flex:1; height:18%; background:var(--blue); border-radius:2px; opacity:0.5;"></div>
            <div style="flex:1; height:12%; background:var(--blue); border-radius:2px; opacity:0.5;"></div>
            <div style="flex:1; height:35%; background:var(--blue); border-radius:2px; opacity:0.5;"></div>
            <div style="flex:1; height:45%; background:var(--blue); border-radius:2px; opacity:0.5;"></div>
            <div style="flex:1; height:50%; background:var(--blue); border-radius:2px; opacity:0.5;"></div>
            <div style="flex:1; height:60%; background:var(--blue); border-radius:2px; opacity:0.8;"></div>
            <div style="flex:1; height:75%; background:var(--blue); border-radius:2px; opacity:0.8;"></div>
            <div style="flex:1; height:85%; background:var(--blue); border-radius:2px; opacity:0.8;"></div>
            <div style="flex:1; height:65%; background:var(--blue); border-radius:2px; opacity:0.8;"></div>
            <div style="flex:1; height:80%; background:var(--blue); border-radius:2px; box-shadow:0 0 10px var(--blue);"></div> <!-- active bar -->
            <div style="flex:1; height:50%; background:var(--blue); border-radius:2px; opacity:0.5;"></div>
            <div style="flex:1; height:30%; background:var(--blue); border-radius:2px; opacity:0.5;"></div>
            <div style="flex:1; height:15%; background:var(--blue); border-radius:2px; opacity:0.5;"></div>
            <div style="flex:1; height:10%; background:var(--blue); border-radius:2px; opacity:0.5;"></div>
          </div>
          <!-- X Axis -->
          <div style="display:flex; justify-content:space-between; margin-top:8px; font-size:9px; color:var(--text-muted); font-weight:600;">
            <span>12 AM</span><span>4 AM</span><span>8 AM</span><span>12 PM</span><span>4 PM</span><span>8 PM</span><span>12 AM</span>
          </div>
        </div>

        <!-- Top Congested Roads -->
        <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 12px 16px; display: flex; flex-direction: column;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom:16px;">
            <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">TOP CONGESTED ROADS</span>
            <span style="font-size:10px; color:var(--blue); cursor:pointer;">View All</span>
          </div>
          <div style="display:flex; flex-direction:column; gap:12px; flex:1;">
            
            <div style="display:flex; align-items:center; gap:16px;">
              <span style="width:70px; font-size:11px; color:var(--text-100);">Anna Salai</span>
              <div style="flex:1; height:4px; background:rgba(255,255,255,0.05); border-radius:2px;">
                <div style="width:82%; height:100%; background:var(--red); border-radius:2px; box-shadow:0 0 8px rgba(239,68,68,0.5);"></div>
              </div>
              <span style="font-size:11px; font-weight:600; color:var(--text-100);">82%</span>
            </div>

            <div style="display:flex; align-items:center; gap:16px;">
              <span style="width:70px; font-size:11px; color:var(--text-100);">Mount Road</span>
              <div style="flex:1; height:4px; background:rgba(255,255,255,0.05); border-radius:2px;">
                <div style="width:71%; height:100%; background:#f97316; border-radius:2px;"></div>
              </div>
              <span style="font-size:11px; font-weight:600; color:var(--text-100);">71%</span>
            </div>

            <div style="display:flex; align-items:center; gap:16px;">
              <span style="width:70px; font-size:11px; color:var(--text-100);">GST Road</span>
              <div style="flex:1; height:4px; background:rgba(255,255,255,0.05); border-radius:2px;">
                <div style="width:56%; height:100%; background:var(--amber); border-radius:2px;"></div>
              </div>
              <span style="font-size:11px; font-weight:600; color:var(--text-100);">56%</span>
            </div>

            <div style="display:flex; align-items:center; gap:16px;">
              <span style="width:70px; font-size:11px; color:var(--text-100);">OMR</span>
              <div style="flex:1; height:4px; background:rgba(255,255,255,0.05); border-radius:2px;">
                <div style="width:48%; height:100%; background:var(--green); border-radius:2px;"></div>
              </div>
              <span style="font-size:11px; font-weight:600; color:var(--text-100);">48%</span>
            </div>

          </div>
        </div>

        <!-- System Status -->
        <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 12px 16px; display: flex; flex-direction: column;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom:16px;">
            <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">SYSTEM STATUS</span>
            <span style="font-size:10px; color:var(--blue); cursor:pointer;">View All</span>
          </div>
          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:12px; flex:1;">
            
            <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.05); border-radius:8px; padding:12px; display:flex; align-items:center; gap:12px;">
              <div style="color:var(--green);"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"/><line x1="12" y1="18" x2="12.01" y2="18"/></svg></div>
              <div style="flex:1;">
                <div style="font-size:11px; font-weight:600; color:var(--text-100);">ANPR System</div>
                <div style="font-size:10px; color:var(--green);">Online</div>
              </div>
              <div style="width:6px; height:6px; border-radius:50%; background:var(--green); box-shadow:0 0 4px var(--green);"></div>
            </div>

            <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.05); border-radius:8px; padding:12px; display:flex; align-items:center; gap:12px;">
              <div style="color:var(--green);"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a10 10 0 1 0 10 10H12V2z"/><path d="M12 12 2.1 7.1"/></svg></div>
              <div style="flex:1;">
                <div style="font-size:11px; font-weight:600; color:var(--text-100);">AI Analytics</div>
                <div style="font-size:10px; color:var(--green);">Online</div>
              </div>
              <div style="width:6px; height:6px; border-radius:50%; background:var(--green); box-shadow:0 0 4px var(--green);"></div>
            </div>

            <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.05); border-radius:8px; padding:12px; display:flex; align-items:center; gap:12px;">
              <div style="color:var(--green);"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg></div>
              <div style="flex:1;">
                <div style="font-size:11px; font-weight:600; color:var(--text-100);">Database</div>
                <div style="font-size:10px; color:var(--green);">Online</div>
              </div>
              <div style="width:6px; height:6px; border-radius:50%; background:var(--green); box-shadow:0 0 4px var(--green);"></div>
            </div>

            <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.05); border-radius:8px; padding:12px; display:flex; align-items:center; gap:12px;">
              <div style="color:var(--green);"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12.55a11 11 0 0 1 14.08 0"/><path d="M1.42 9a16 16 0 0 1 21.16 0"/><path d="M8.53 16.11a6 6 0 0 1 6.95 0"/><line x1="12" y1="20" x2="12.01" y2="20"/></svg></div>
              <div style="flex:1;">
                <div style="font-size:11px; font-weight:600; color:var(--text-100);">Network</div>
                <div style="font-size:10px; color:var(--green);">Stable</div>
              </div>
              <div style="width:6px; height:6px; border-radius:50%; background:var(--green); box-shadow:0 0 4px var(--green);"></div>
            </div>

          </div>
        </div>

      </div>

    </div>
  `;
}

export function initDashboardMap() {
  const mapContainer = document.getElementById('leaflet-map');
  if (!mapContainer || mapContainer._leaflet_id) return; // Prevent double init
  
  // Center map roughly on Chennai with zoom level 12
  const map = L.map('leaflet-map', {
    zoomControl: false,
    attributionControl: false
  }).setView([13.0410, 80.2345], 12);
  
  // Use standard OpenStreetMap tiles with a CSS filter to make it dark and avoid API keys
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    className: 'dark-map-tiles'
  }).addTo(map);

  // Add zoom control to top right
  L.control.zoom({ position: 'topright' }).addTo(map);

  // Draw some dummy polylines for traffic flow
  const p1 = [[13.06, 80.2], [13.05, 80.22], [13.04, 80.24]]; // smooth
  const p2 = [[13.04, 80.24], [13.02, 80.25], [13.01, 80.26]]; // moderate
  const p3 = [[13.01, 80.26], [13.00, 80.25], [12.98, 80.24]]; // heavy
  const p4 = [[12.98, 80.24], [12.97, 80.23], [12.96, 80.22]]; // severe
  
  L.polyline(p1, { color: '#22c55e', weight: 4 }).addTo(map);
  L.polyline(p2, { color: '#f59e0b', weight: 4 }).addTo(map);
  L.polyline(p3, { color: '#f97316', weight: 4 }).addTo(map);
  L.polyline(p4, { color: '#ef4444', weight: 4 }).addTo(map);

  // Add dummy warning markers (custom SVG icon)
  const warningIcon = L.divIcon({
    html: `<svg width="24" height="24" viewBox="0 0 24 24" fill="#f59e0b" stroke="#000" stroke-width="2"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13" stroke="#000"/><line x1="12" y1="17" x2="12.01" y2="17" stroke="#000"/></svg>`,
    className: '',
    iconSize: [24, 24],
    iconAnchor: [12, 12]
  });
  
  L.marker([13.04, 80.24], { icon: warningIcon }).addTo(map).bindPopup("Congestion reported");

  // Fetch live cameras and add them to the map
  const camIcon = L.divIcon({
    html: `<svg width="24" height="24" viewBox="0 0 24 24" fill="#3b82f6" stroke="#fff" stroke-width="2"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>`,
    className: '',
    iconSize: [24, 24],
    iconAnchor: [12, 12]
  });

  const backendUrl = (import.meta.env.VITE_BACKEND_URL || '').replace(/\/$/, '');
  fetch(`${backendUrl}/api/v1/cameras/sessions`).then(res => {
    if(res.ok) return res.json();
    return [];
  }).then(sessions => {
    let centered = false;
    sessions.forEach(session => {
      if (session.latitude && session.longitude) {
        L.marker([session.latitude, session.longitude], { icon: camIcon })
          .addTo(map)
          .bindPopup(`<b>CAM-${session.session_id.substring(0, 4).toUpperCase()}</b><br>Live Stream`);
          
        if (!centered) {
          map.setView([session.latitude, session.longitude], 13);
          centered = true;
        }
      }
    });
  }).catch(e => console.error("Failed to load cameras for dashboard map", e));
  
  L.marker([13.01, 80.22], { icon: warningIcon }).addTo(map);
}
