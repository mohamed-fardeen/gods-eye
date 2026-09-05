export function renderTraffic() {
  return `
    <div style="padding: 24px; display: flex; flex-direction: column; gap: 20px; height: 100%; overflow-y: auto;">
      
      <!-- Top Header & Dropdowns -->
      <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <div>
          <h1 style="font-size:18px; font-weight:700; color:#fff; text-transform:uppercase; letter-spacing:0.5px; margin:0 0 4px 0;">TRAFFIC ANALYSIS</h1>
          <div style="font-size:11px; color:var(--text-muted);">Real-time traffic insights and historical trends</div>
        </div>
        <div style="display:flex; gap:12px;">
          <div style="background:rgba(12,17,32,0.9); border:1px solid rgba(255,255,255,0.1); border-radius:6px; padding:6px 12px; display:flex; align-items:center; gap:8px; font-size:11px; color:var(--text-200); cursor:pointer;">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
            21 May 2024
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m6 9 6 6 6-6"/></svg>
          </div>
          <div style="background:rgba(12,17,32,0.9); border:1px solid rgba(255,255,255,0.1); border-radius:6px; padding:6px 12px; display:flex; align-items:center; gap:8px; font-size:11px; color:var(--text-200); cursor:pointer;">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            Last 24 Hours
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m6 9 6 6-6"/></svg>
          </div>
          <div style="background:rgba(12,17,32,0.9); border:1px solid rgba(255,255,255,0.1); border-radius:6px; padding:6px 12px; display:flex; align-items:center; gap:8px; font-size:11px; color:var(--text-200); cursor:pointer;">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
            All Zones
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m6 9 6 6 6-6"/></svg>
          </div>
        </div>
      </div>

      <!-- KPIs Row -->
      <div style="display:grid; grid-template-columns:repeat(6, 1fr); gap:12px;">
        <div style="background:rgba(12,17,32,0.9); border:1px solid rgba(255,255,255,0.07); border-radius:8px; padding:12px 16px; display:flex; align-items:center; gap:16px;">
          <div style="color:var(--blue);"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><path d="m9 15 2 2 4-4"/></svg></div>
          <div>
            <div style="font-size:10px; color:var(--blue); text-transform:uppercase; font-weight:600; margin-bottom:4px;">TOTAL VEHICLES</div>
            <div style="font-size:20px; font-weight:700; color:#fff; line-height:1;">148,726</div>
            <div style="font-size:9px; color:var(--green); margin-top:4px;">&uarr; 12.4% <span style="color:var(--text-muted);">vs yesterday</span></div>
          </div>
        </div>
        
        <div style="background:rgba(12,17,32,0.9); border:1px solid rgba(255,255,255,0.07); border-radius:8px; padding:12px 16px; display:flex; align-items:center; gap:16px;">
          <div style="color:var(--blue);"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 2a10 10 0 0 1 10 10"/><path d="m12 12 4-4"/></svg></div>
          <div>
            <div style="font-size:10px; color:var(--blue); text-transform:uppercase; font-weight:600; margin-bottom:4px;">AVG SPEED</div>
            <div style="font-size:20px; font-weight:700; color:#fff; line-height:1;">24.6 <span style="font-size:12px; font-weight:500;">km/h</span></div>
            <div style="font-size:9px; color:var(--red); margin-top:4px;">&darr; 8.6% <span style="color:var(--text-muted);">vs yesterday</span></div>
          </div>
        </div>

        <div style="background:rgba(12,17,32,0.9); border:1px solid rgba(255,255,255,0.07); border-radius:8px; padding:12px 16px; display:flex; align-items:center; gap:16px;">
          <div style="color:var(--blue);"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/></svg></div>
          <div>
            <div style="font-size:10px; color:var(--blue); text-transform:uppercase; font-weight:600; margin-bottom:4px;">TOTAL TRIPS</div>
            <div style="font-size:20px; font-weight:700; color:#fff; line-height:1;">96,432</div>
            <div style="font-size:9px; color:var(--green); margin-top:4px;">&uarr; 9.7% <span style="color:var(--text-muted);">vs yesterday</span></div>
          </div>
        </div>

        <div style="background:rgba(12,17,32,0.9); border:1px solid rgba(255,255,255,0.07); border-radius:8px; padding:12px 16px; display:flex; align-items:center; gap:16px;">
          <div style="color:var(--orange);"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="2" width="6" height="20" rx="3"/><circle cx="12" cy="7" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="12" cy="17" r="1"/></svg></div>
          <div>
            <div style="font-size:10px; color:var(--red); text-transform:uppercase; font-weight:600; margin-bottom:4px;">CONGESTION INDEX</div>
            <div style="font-size:20px; font-weight:700; color:#fff; line-height:1;">0.78</div>
            <div style="font-size:9px; color:var(--orange); margin-top:4px; font-weight:600;">High</div>
          </div>
        </div>

        <div style="background:rgba(12,17,32,0.9); border:1px solid rgba(255,255,255,0.07); border-radius:8px; padding:12px 16px; display:flex; align-items:center; gap:16px;">
          <div style="color:var(--purple);"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg></div>
          <div>
            <div style="font-size:10px; color:var(--purple); text-transform:uppercase; font-weight:600; margin-bottom:4px;">DELAY TIME</div>
            <div style="font-size:20px; font-weight:700; color:#fff; line-height:1;">18h 42m</div>
            <div style="font-size:9px; color:var(--green); margin-top:4px;">&uarr; 15.3% <span style="color:var(--text-muted);">vs yesterday</span></div>
          </div>
        </div>

        <div style="background:rgba(12,17,32,0.9); border:1px solid rgba(255,255,255,0.07); border-radius:8px; padding:12px 16px; display:flex; align-items:center; gap:16px;">
          <div style="color:var(--red);"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg></div>
          <div>
            <div style="font-size:10px; color:var(--red); text-transform:uppercase; font-weight:600; margin-bottom:4px;">INCIDENTS</div>
            <div style="font-size:20px; font-weight:700; color:#fff; line-height:1;">23</div>
            <div style="font-size:9px; color:var(--green); margin-top:4px;">&uarr; 4 <span style="color:var(--text-muted);">vs yesterday</span></div>
          </div>
        </div>
      </div>

      <!-- Main 3-Column Grid -->
      <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:16px; flex:1; min-height:0;">
        
        <!-- COLUMN 1 -->
        <div style="display:flex; flex-direction:column; gap:16px;">
          <!-- Heatmap -->
          <div style="background:rgba(12,17,32,0.9); border:1px solid rgba(255,255,255,0.07); border-radius:12px; display:flex; flex-direction:column; overflow:hidden; flex:1.5; min-height:280px; position:relative;">
            <div style="padding:16px; position:absolute; z-index:2; width:100%; pointer-events:none;">
              <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">TRAFFIC HEATMAP <span style="font-weight:400; text-transform:none;">(Live)</span></span>
            </div>
            <div id="traffic-map-heatmap" style="flex:1; width:100%; background:#000;"></div>
            
            <!-- Floating Legend -->
            <div style="position:absolute; bottom:16px; left:16px; right:16px; display:flex; justify-content:space-between; align-items:center; z-index:2; font-size:9px; color:var(--text-200); pointer-events:none;">
              <div style="display:flex; gap:12px;">
                <span style="display:flex; align-items:center; gap:4px;"><span style="width:12px; height:3px; background:var(--green); border-radius:2px;"></span> Smooth</span>
                <span style="display:flex; align-items:center; gap:4px;"><span style="width:12px; height:3px; background:var(--amber); border-radius:2px;"></span> Moderate</span>
                <span style="display:flex; align-items:center; gap:4px;"><span style="width:12px; height:3px; background:var(--orange); border-radius:2px;"></span> Heavy</span>
                <span style="display:flex; align-items:center; gap:4px;"><span style="width:12px; height:3px; background:var(--red); border-radius:2px;"></span> Severe</span>
                <span style="display:flex; align-items:center; gap:4px;"><span style="width:12px; height:3px; background:var(--text-muted); border-radius:2px;"></span> No Data</span>
              </div>
            </div>
          </div>
          
          <!-- Avg Speed By Road -->
          <div style="background:rgba(12,17,32,0.9); border:1px solid rgba(255,255,255,0.07); border-radius:12px; padding:16px; flex:1;">
            <div style="display:flex; justify-content:space-between; margin-bottom:16px;">
              <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">AVERAGE SPEED BY ROAD</span>
              <span style="font-size:10px; color:var(--blue);">km/h</span>
            </div>
            <div style="display:flex; flex-direction:column; gap:10px;">
              <div style="display:flex; align-items:center; justify-content:space-between; font-size:10px;">
                <div style="width:120px; color:var(--text-200);">OMR (IT Expressway)</div>
                <div style="flex:1; background:rgba(255,255,255,0.05); height:6px; border-radius:3px; margin:0 12px; position:relative;">
                  <div style="position:absolute; left:0; top:0; bottom:0; width:85%; background:var(--green); border-radius:3px;"></div>
                </div>
                <div style="width:24px; text-align:right; color:#fff; font-weight:600;">46.3</div>
              </div>
              <div style="display:flex; align-items:center; justify-content:space-between; font-size:10px;">
                <div style="width:120px; color:var(--text-200);">GST Road</div>
                <div style="flex:1; background:rgba(255,255,255,0.05); height:6px; border-radius:3px; margin:0 12px; position:relative;">
                  <div style="position:absolute; left:0; top:0; bottom:0; width:65%; background:var(--green); border-radius:3px;"></div>
                </div>
                <div style="width:24px; text-align:right; color:#fff; font-weight:600;">34.8</div>
              </div>
              <div style="display:flex; align-items:center; justify-content:space-between; font-size:10px;">
                <div style="width:120px; color:var(--text-200);">ECR (East Coast Road)</div>
                <div style="flex:1; background:rgba(255,255,255,0.05); height:6px; border-radius:3px; margin:0 12px; position:relative;">
                  <div style="position:absolute; left:0; top:0; bottom:0; width:50%; background:var(--amber); border-radius:3px;"></div>
                </div>
                <div style="width:24px; text-align:right; color:#fff; font-weight:600;">28.9</div>
              </div>
              <div style="display:flex; align-items:center; justify-content:space-between; font-size:10px;">
                <div style="width:120px; color:var(--text-200);">Mount Road</div>
                <div style="flex:1; background:rgba(255,255,255,0.05); height:6px; border-radius:3px; margin:0 12px; position:relative;">
                  <div style="position:absolute; left:0; top:0; bottom:0; width:35%; background:var(--orange); border-radius:3px;"></div>
                </div>
                <div style="width:24px; text-align:right; color:#fff; font-weight:600;">22.1</div>
              </div>
              <div style="display:flex; align-items:center; justify-content:space-between; font-size:10px;">
                <div style="width:120px; color:var(--text-200);">Anna Salai</div>
                <div style="flex:1; background:rgba(255,255,255,0.05); height:6px; border-radius:3px; margin:0 12px; position:relative;">
                  <div style="position:absolute; left:0; top:0; bottom:0; width:20%; background:var(--red); border-radius:3px;"></div>
                </div>
                <div style="width:24px; text-align:right; color:#fff; font-weight:600;">17.6</div>
              </div>
            </div>
          </div>

          <!-- Traffic Forecast -->
          <div style="background:rgba(12,17,32,0.9); border:1px solid rgba(255,255,255,0.07); border-radius:12px; padding:16px; flex:1; display:flex; flex-direction:column;">
            <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
              <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">TRAFFIC FORECAST <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-left:4px;"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg></span>
            </div>
            <div style="font-size:9px; color:var(--text-dim); margin-bottom:12px;">Predicted congestion for next 3 hours</div>
            
            <div style="display:flex; gap:16px; flex:1;">
              <div style="flex:1; position:relative; display:flex; flex-direction:column;">
                <!-- Chart Y Axis -->
                <div style="position:absolute; left:0; top:0; bottom:20px; display:flex; flex-direction:column; justify-content:space-between; font-size:8px; color:var(--text-dim);">
                  <span>High</span><span>Medium</span><span>Low</span>
                </div>
                <!-- Chart Area (fake SVG line) -->
                <div style="margin-left:36px; flex:1; position:relative;">
                  <svg viewBox="0 0 100 50" preserveAspectRatio="none" style="position:absolute; inset:0; width:100%; height:100%;">
                    <defs>
                      <linearGradient id="forecastGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stop-color="rgba(245,158,11,0.3)"/>
                        <stop offset="100%" stop-color="rgba(245,158,11,0)"/>
                      </linearGradient>
                    </defs>
                    <path d="M0,50 L0,30 L15,15 L30,10 L45,25 L60,15 L75,35 L90,25 L100,20 L100,50 Z" fill="url(#forecastGrad)"/>
                    <polyline points="0,30 15,15 30,10 45,25 60,15 75,35 90,25 100,20" fill="none" stroke="var(--orange)" stroke-width="2"/>
                    <circle cx="15" cy="15" r="2" fill="var(--orange)"/>
                    <circle cx="30" cy="10" r="2" fill="var(--orange)"/>
                    <circle cx="45" cy="25" r="2" fill="var(--orange)"/>
                    <circle cx="60" cy="15" r="2" fill="var(--orange)"/>
                    <circle cx="75" cy="35" r="2" fill="var(--orange)"/>
                    <circle cx="90" cy="25" r="2" fill="var(--orange)"/>
                  </svg>
                </div>
                <!-- Chart X Axis -->
                <div style="margin-left:36px; display:flex; justify-content:space-between; font-size:8px; color:var(--text-dim); margin-top:4px;">
                  <span>Now</span><span>+30m</span><span>+1h</span><span>+1.5h</span><span>+2h</span><span>+2.5h</span><span>+3h</span>
                </div>
              </div>
              
              <div style="width:110px; display:flex; flex-direction:column; gap:12px; justify-content:center;">
                <div>
                  <div style="font-size:9px; color:var(--text-dim);">Peak Congestion</div>
                  <div style="display:flex; justify-content:space-between; align-items:center; margin-top:2px;">
                    <span style="font-size:9px; color:#fff;">Today at 06:15 PM</span>
                    <span style="background:rgba(239,68,68,0.2); color:var(--red); padding:2px 4px; border-radius:4px; font-size:8px; font-weight:700;">High</span>
                  </div>
                </div>
                <div>
                  <div style="font-size:9px; color:var(--text-dim);">Expected Delay</div>
                  <div style="display:flex; justify-content:space-between; align-items:baseline; margin-top:2px;">
                    <span style="font-size:12px; font-weight:700; color:#fff;">+23 min</span>
                    <span style="font-size:8px; color:var(--text-dim);">vs usual</span>
                  </div>
                </div>
                <div style="display:flex; gap:6px; align-items:flex-start; margin-top:4px;">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--green)" stroke-width="2" style="margin-top:2px;"><circle cx="12" cy="12" r="10"/><polyline points="12 16 12 12 12 8"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                  <div>
                    <div style="font-size:8px; color:var(--text-dim);">Recommended Action</div>
                    <div style="font-size:9px; color:var(--text-200);">Adjust signal timing in 5 zones</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- COLUMN 2 -->
        <div style="display:flex; flex-direction:column; gap:16px;">
          <!-- Traffic Volume Over Time -->
          <div style="background:rgba(12,17,32,0.9); border:1px solid rgba(255,255,255,0.07); border-radius:12px; padding:16px; flex:1.2; display:flex; flex-direction:column;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
              <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">TRAFFIC VOLUME OVER TIME</span>
              <div style="font-size:9px; color:var(--text-200); display:flex; align-items:center; gap:4px; cursor:pointer;">
                By Vehicle Type <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m6 9 6 6 6-6"/></svg>
              </div>
            </div>
            
            <div style="flex:1; display:flex; flex-direction:column; position:relative;">
              <div style="position:absolute; left:0; top:0; bottom:20px; display:flex; flex-direction:column; justify-content:space-between; font-size:8px; color:var(--text-dim);">
                <span>5K</span><span>4K</span><span>3K</span><span>2K</span><span>1K</span><span>0</span>
              </div>
              <div style="margin-left:20px; flex:1; position:relative;">
                <!-- Stacked area chart representation -->
                <svg viewBox="0 0 100 100" preserveAspectRatio="none" style="position:absolute; inset:0; width:100%; height:100%;">
                  <!-- Trucks (Red base) -->
                  <path d="M0,100 L0,95 L15,90 L30,95 L40,85 L50,60 L60,85 L70,95 L80,60 L90,85 L100,95 L100,100 Z" fill="var(--red)" opacity="0.9"/>
                  <!-- Buses (Yellow) -->
                  <path d="M0,95 L0,90 L15,80 L30,90 L40,75 L50,45 L60,75 L70,90 L80,45 L90,75 L100,90 L100,95 Z" fill="var(--amber)" opacity="0.9"/>
                  <!-- Two Wheelers (Green) -->
                  <path d="M0,90 L0,80 L15,65 L30,80 L40,60 L50,25 L60,60 L70,80 L80,25 L90,60 L100,80 L100,90 Z" fill="var(--green)" opacity="0.9"/>
                  <!-- Cars (Blue) -->
                  <path d="M0,80 L0,65 L15,45 L30,65 L40,40 L50,5 L60,40 L70,65 L80,5 L90,40 L100,65 L100,80 Z" fill="var(--blue)" opacity="0.9"/>
                </svg>
              </div>
              <div style="margin-left:20px; display:flex; justify-content:space-between; font-size:8px; color:var(--text-dim); margin-top:6px;">
                <span>12 AM</span><span>3 AM</span><span>6 AM</span><span>9 AM</span><span>12 PM</span><span>3 PM</span><span>6 PM</span><span>9 PM</span><span>12 AM</span>
              </div>
            </div>
            
            <!-- Chart Legend -->
            <div style="display:flex; justify-content:center; gap:16px; margin-top:12px; font-size:9px; color:var(--text-200);">
              <span style="display:flex; align-items:center; gap:4px;"><span style="width:10px; height:6px; background:var(--blue); border-radius:2px;"></span> Cars</span>
              <span style="display:flex; align-items:center; gap:4px;"><span style="width:10px; height:6px; background:var(--green); border-radius:2px;"></span> Two Wheelers</span>
              <span style="display:flex; align-items:center; gap:4px;"><span style="width:10px; height:6px; background:var(--amber); border-radius:2px;"></span> Buses</span>
              <span style="display:flex; align-items:center; gap:4px;"><span style="width:10px; height:6px; background:var(--red); border-radius:2px;"></span> Trucks</span>
            </div>
          </div>

          <!-- Density By Time of Day -->
          <div style="background:rgba(12,17,32,0.9); border:1px solid rgba(255,255,255,0.07); border-radius:12px; padding:16px; flex:1; display:flex; flex-direction:column;">
            <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px; margin-bottom:16px;">TRAFFIC DENSITY BY TIME OF DAY</span>
            <div style="flex:1; display:flex;">
              <div style="display:flex; flex-direction:column; justify-content:space-around; font-size:9px; color:var(--text-dim); width:24px; padding-bottom:16px;">
                <span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span><span>Fri</span><span>Sat</span><span>Sun</span>
              </div>
              <div style="flex:1; display:flex; flex-direction:column;">
                <div style="flex:1; display:grid; grid-template-columns:repeat(12, 1fr); gap:2px;">
                  ${Array.from({length:7}).map((_, r) => 
                    Array.from({length:12}).map((_, c) => {
                      let intensity = 0;
                      if (r < 5) {
                        if (c === 4 || c === 5 || c === 8 || c === 9) intensity = 0.8 + Math.random()*0.2; // Peak
                        else if (c === 3 || c === 6 || c === 7 || c === 10) intensity = 0.4 + Math.random()*0.3; // Mid
                        else intensity = 0.1 + Math.random()*0.2; // Low
                      } else {
                        if (c > 5 && c < 10) intensity = 0.5 + Math.random()*0.3; // Weekend peak
                        else intensity = 0.1 + Math.random()*0.2;
                      }
                      let color = `rgba(34,197,94,${intensity})`;
                      if (intensity > 0.4) color = `rgba(245,158,11,${intensity})`;
                      if (intensity > 0.7) color = `rgba(239,68,68,${intensity})`;
                      return `<div style="background:${color}; border-radius:1px; width:100%; height:100%;"></div>`;
                    }).join('')
                  ).join('')}
                </div>
                <div style="display:flex; justify-content:space-between; font-size:8px; color:var(--text-dim); margin-top:6px;">
                  <span>12 AM</span><span>3 AM</span><span>6 AM</span><span>9 AM</span><span>12 PM</span><span>3 PM</span><span>6 PM</span><span>9 PM</span><span>12 AM</span>
                </div>
              </div>
            </div>
            <div style="display:flex; justify-content:center; align-items:center; gap:8px; margin-top:12px;">
              <span style="font-size:9px; color:var(--text-dim);">Low</span>
              <div style="width:100px; height:4px; border-radius:2px; background:linear-gradient(90deg, rgba(34,197,94,0.3), rgba(245,158,11,0.6), rgba(239,68,68,0.9));"></div>
              <span style="font-size:9px; color:var(--text-dim);">High</span>
            </div>
          </div>

          <!-- Incident Impact -->
          <div style="background:rgba(12,17,32,0.9); border:1px solid rgba(255,255,255,0.07); border-radius:12px; padding:16px; flex:1; display:flex; flex-direction:column;">
            <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
              <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">INCIDENT IMPACT ANALYSIS</span>
              <span style="font-size:9px; color:var(--blue); cursor:pointer;">View Report</span>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; flex:1;">
              
              <div style="text-align:center;">
                <div style="font-size:9px; color:var(--text-dim); margin-bottom:4px;">Incidents Today</div>
                <div style="font-size:24px; font-weight:700; color:#fff; line-height:1;">23</div>
                <div style="font-size:9px; color:var(--green); margin-top:4px;">&uarr; 4 <span style="color:var(--text-muted);">vs yesterday</span></div>
              </div>

              <div style="width:1px; height:40px; background:rgba(255,255,255,0.1);"></div>

              <div style="display:flex; flex-direction:column; align-items:center;">
                <div style="font-size:9px; color:var(--text-dim); margin-bottom:4px;">Impact On Traffic</div>
                <div style="position:relative; width:48px; height:48px;">
                  <svg viewBox="0 0 36 36" style="transform:rotate(-90deg); width:48px; height:48px;">
                    <circle cx="18" cy="18" r="15.915" fill="transparent" stroke="rgba(255,255,255,0.1)" stroke-width="4"></circle>
                    <circle cx="18" cy="18" r="15.915" fill="transparent" stroke="var(--orange)" stroke-width="4" stroke-dasharray="28, 72"></circle>
                  </svg>
                  <div style="position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center;">
                    <span style="font-size:11px; font-weight:700; color:#fff;">28%</span>
                  </div>
                </div>
                <div style="font-size:8px; color:var(--orange); font-weight:600; margin-top:2px;">High Impact</div>
              </div>

              <div style="width:1px; height:40px; background:rgba(255,255,255,0.1);"></div>

              <div style="display:flex; flex-direction:column; gap:12px;">
                <div>
                  <div style="font-size:9px; color:var(--text-dim); margin-bottom:2px;">Total Affected Distance</div>
                  <div style="font-size:14px; font-weight:600; color:#fff;">36.8 km</div>
                  <div style="font-size:8px; color:var(--green);">&uarr; 12.4% <span style="color:var(--text-muted);">vs yesterday</span></div>
                </div>
                <div>
                  <div style="font-size:9px; color:var(--text-dim); margin-bottom:2px;">Total Delay Caused</div>
                  <div style="font-size:14px; font-weight:600; color:#fff;">6h 37m</div>
                  <div style="font-size:8px; color:var(--red);">&uarr; 18.7% <span style="color:var(--text-muted);">vs yesterday</span></div>
                </div>
              </div>

            </div>
          </div>
        </div>

        <!-- COLUMN 3 -->
        <div style="display:flex; flex-direction:column; gap:16px;">
          <!-- Traffic By Vehicle Type -->
          <div style="background:rgba(12,17,32,0.9); border:1px solid rgba(255,255,255,0.07); border-radius:12px; padding:16px; flex:1.2; display:flex; flex-direction:column;">
            <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px; margin-bottom:16px;">TRAFFIC BY VEHICLE TYPE</span>
            
            <div style="display:flex; align-items:center; justify-content:space-around; flex:1;">
              <!-- Donut Chart -->
              <div style="position:relative; width:120px; height:120px;">
                <svg viewBox="0 0 36 36" style="width:120px; height:120px; transform:rotate(-90deg);">
                  <!-- Trucks (6.9%) -->
                  <circle cx="18" cy="18" r="14" fill="transparent" stroke="var(--red)" stroke-width="5" stroke-dasharray="6.9, 93.1" stroke-dashoffset="0"></circle>
                  <!-- Buses (7.1%) -->
                  <circle cx="18" cy="18" r="14" fill="transparent" stroke="var(--amber)" stroke-width="5" stroke-dasharray="7.1, 92.9" stroke-dashoffset="-6.9"></circle>
                  <!-- Two Wheelers (33.6%) -->
                  <circle cx="18" cy="18" r="14" fill="transparent" stroke="var(--green)" stroke-width="5" stroke-dasharray="33.6, 66.4" stroke-dashoffset="-14"></circle>
                  <!-- Cars (52.4%) -->
                  <circle cx="18" cy="18" r="14" fill="transparent" stroke="var(--blue)" stroke-width="5" stroke-dasharray="52.4, 47.6" stroke-dashoffset="-47.6"></circle>
                </svg>
                <div style="position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center;">
                  <span style="font-size:9px; color:var(--text-dim); text-transform:uppercase;">TOTAL</span>
                  <span style="font-size:14px; font-weight:700; color:#fff;">148,726</span>
                </div>
              </div>

              <!-- Legend Details -->
              <div style="display:flex; flex-direction:column; gap:12px; font-size:10px;">
                <div style="display:flex; align-items:center; gap:8px;">
                  <span style="width:8px; height:8px; border-radius:50%; background:var(--blue);"></span>
                  <span style="color:var(--text-200); width:70px;">Cars</span>
                  <span style="color:#fff; font-weight:600; width:30px; text-align:right;">52.4%</span>
                  <span style="color:var(--text-dim);">(77,898)</span>
                </div>
                <div style="display:flex; align-items:center; gap:8px;">
                  <span style="width:8px; height:8px; border-radius:50%; background:var(--green);"></span>
                  <span style="color:var(--text-200); width:70px;">Two Wheelers</span>
                  <span style="color:#fff; font-weight:600; width:30px; text-align:right;">33.6%</span>
                  <span style="color:var(--text-dim);">(49,959)</span>
                </div>
                <div style="display:flex; align-items:center; gap:8px;">
                  <span style="width:8px; height:8px; border-radius:50%; background:var(--amber);"></span>
                  <span style="color:var(--text-200); width:70px;">Buses</span>
                  <span style="color:#fff; font-weight:600; width:30px; text-align:right;">7.1%</span>
                  <span style="color:var(--text-dim);">(10,567)</span>
                </div>
                <div style="display:flex; align-items:center; gap:8px;">
                  <span style="width:8px; height:8px; border-radius:50%; background:var(--red);"></span>
                  <span style="color:var(--text-200); width:70px;">Trucks</span>
                  <span style="color:#fff; font-weight:600; width:30px; text-align:right;">6.9%</span>
                  <span style="color:var(--text-dim);">(10,302)</span>
                </div>
              </div>
            </div>
            
            <div style="margin-top:16px; font-size:10px; color:var(--blue); cursor:pointer;">
              View Detailed Report &rarr;
            </div>
          </div>

          <!-- Congested Zones -->
          <div style="background:rgba(12,17,32,0.9); border:1px solid rgba(255,255,255,0.07); border-radius:12px; padding:16px; flex:1;">
            <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
              <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">CONGESTED ZONES <span style="font-weight:400; text-transform:none;">(Live)</span></span>
              <span style="font-size:9px; color:var(--blue); cursor:pointer;">View All</span>
            </div>
            <table style="width:100%; border-collapse:collapse; font-size:10px; text-align:left;">
              <thead>
                <tr style="color:var(--text-dim); border-bottom:1px solid rgba(255,255,255,0.05);">
                  <th style="padding:6px 4px; font-weight:500;">#</th>
                  <th style="padding:6px 4px; font-weight:500;">Zone / Road</th>
                  <th style="padding:6px 4px; font-weight:500;">Congestion Index</th>
                  <th style="padding:6px 4px; font-weight:500;">Avg Speed</th>
                  <th style="padding:6px 4px; font-weight:500;">Status</th>
                </tr>
              </thead>
              <tbody style="color:var(--text-200);">
                <tr style="border-bottom:1px solid rgba(255,255,255,0.02);">
                  <td style="padding:8px 4px;">1</td><td style="padding:8px 4px;">Anna Salai (T. Nagar)</td><td style="padding:8px 4px; color:var(--red);">0.92</td><td style="padding:8px 4px;">14 km/h</td>
                  <td style="padding:8px 4px;"><span style="background:rgba(239,68,68,0.2); color:var(--red); padding:2px 6px; border-radius:4px; font-size:8px;">Severe</span></td>
                </tr>
                <tr style="border-bottom:1px solid rgba(255,255,255,0.02);">
                  <td style="padding:8px 4px;">2</td><td style="padding:8px 4px;">Mount Road</td><td style="padding:8px 4px; color:var(--red);">0.81</td><td style="padding:8px 4px;">18 km/h</td>
                  <td style="padding:8px 4px;"><span style="background:rgba(239,68,68,0.2); color:var(--red); padding:2px 6px; border-radius:4px; font-size:8px;">Severe</span></td>
                </tr>
                <tr style="border-bottom:1px solid rgba(255,255,255,0.02);">
                  <td style="padding:8px 4px;">3</td><td style="padding:8px 4px;">Vadapalani Signal</td><td style="padding:8px 4px; color:var(--orange);">0.76</td><td style="padding:8px 4px;">20 km/h</td>
                  <td style="padding:8px 4px;"><span style="background:rgba(245,158,11,0.2); color:var(--orange); padding:2px 6px; border-radius:4px; font-size:8px;">Heavy</span></td>
                </tr>
                <tr style="border-bottom:1px solid rgba(255,255,255,0.02);">
                  <td style="padding:8px 4px;">4</td><td style="padding:8px 4px;">Nungambakkam High Rd</td><td style="padding:8px 4px; color:var(--orange);">0.69</td><td style="padding:8px 4px;">22 km/h</td>
                  <td style="padding:8px 4px;"><span style="background:rgba(245,158,11,0.2); color:var(--orange); padding:2px 6px; border-radius:4px; font-size:8px;">Heavy</span></td>
                </tr>
                <tr>
                  <td style="padding:8px 4px;">5</td><td style="padding:8px 4px;">OMR (Perungudi)</td><td style="padding:8px 4px; color:var(--amber);">0.45</td><td style="padding:8px 4px;">41 km/h</td>
                  <td style="padding:8px 4px;"><span style="background:rgba(245,158,11,0.2); color:var(--amber); padding:2px 6px; border-radius:4px; font-size:8px;">Moderate</span></td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Origin Destination -->
          <div style="background:rgba(12,17,32,0.9); border:1px solid rgba(255,255,255,0.07); border-radius:12px; padding:16px; flex:1;">
            <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
              <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">TOP ORIGIN - DESTINATION PAIRS</span>
              <span style="font-size:9px; color:var(--blue); cursor:pointer;">View All</span>
            </div>
            <table style="width:100%; border-collapse:collapse; font-size:10px; text-align:left;">
              <thead>
                <tr style="color:var(--text-dim); border-bottom:1px solid rgba(255,255,255,0.05);">
                  <th style="padding:6px 4px; font-weight:500;">From</th>
                  <th style="padding:6px 4px; font-weight:500;">To</th>
                  <th style="padding:6px 4px; font-weight:500;">Trips</th>
                  <th style="padding:6px 4px; font-weight:500;">Avg Time</th>
                </tr>
              </thead>
              <tbody style="color:var(--text-200);">
                <tr style="border-bottom:1px solid rgba(255,255,255,0.02);">
                  <td style="padding:6px 4px;">OMR (Sholinganallur)</td><td style="padding:6px 4px;">Guindy</td><td style="padding:6px 4px;">5,842</td><td style="padding:6px 4px;">28 min</td>
                </tr>
                <tr style="border-bottom:1px solid rgba(255,255,255,0.02);">
                  <td style="padding:6px 4px;">Anna Nagar</td><td style="padding:6px 4px;">T. Nagar</td><td style="padding:6px 4px;">4,982</td><td style="padding:6px 4px;">24 min</td>
                </tr>
                <tr style="border-bottom:1px solid rgba(255,255,255,0.02);">
                  <td style="padding:6px 4px;">Velachery</td><td style="padding:6px 4px;">OMR (Perungudi)</td><td style="padding:6px 4px;">4,321</td><td style="padding:6px 4px;">32 min</td>
                </tr>
                <tr style="border-bottom:1px solid rgba(255,255,255,0.02);">
                  <td style="padding:6px 4px;">Adyar</td><td style="padding:6px 4px;">T. Nagar</td><td style="padding:6px 4px;">3,876</td><td style="padding:6px 4px;">20 min</td>
                </tr>
                <tr>
                  <td style="padding:6px 4px;">Guindy</td><td style="padding:6px 4px;">Anna Nagar</td><td style="padding:6px 4px;">3,421</td><td style="padding:6px 4px;">26 min</td>
                </tr>
              </tbody>
            </table>
          </div>

        </div>

      </div>

    </div>
  `;
}

export function initTrafficMap() {
  const mapContainer = document.getElementById('traffic-map-heatmap');
  if (!mapContainer || mapContainer._leaflet_id) return;
  
  const map = L.map('traffic-map-heatmap', {
    zoomControl: false,
    attributionControl: false
  }).setView([13.06, 80.25], 11); 
  
  L.control.zoom({ position: 'topright' }).addTo(map);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    className: 'dark-map-tiles'
  }).addTo(map);

  const drawTrafficLine = (coords, color, weight=3) => {
    L.polyline(coords, { color, weight, opacity: 0.8 }).addTo(map);
  };

  // Fake lines for Anna Salai / Mount Road
  drawTrafficLine([[13.0827, 80.2707], [13.0622, 80.2484]], 'var(--red)', 4); // Severe
  drawTrafficLine([[13.0622, 80.2484], [13.04, 80.23]], 'var(--orange)', 3); // Heavy
  drawTrafficLine([[13.04, 80.23], [13.01, 80.21]], 'var(--amber)', 3); // Moderate
  
  // Fake lines for OMR
  drawTrafficLine([[13.00, 80.25], [12.98, 80.25]], 'var(--green)', 3); // Smooth
  drawTrafficLine([[12.98, 80.25], [12.95, 80.24]], 'var(--green)', 3); 

  // Alerts on map
  const alertIcon = L.divIcon({
    html: `<div style="color:var(--red); filter:drop-shadow(0 2px 4px rgba(0,0,0,0.8));">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="var(--red)" stroke="#000" stroke-width="2">
              <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
              <line x1="12" y1="9" x2="12" y2="13" stroke="#000"/><line x1="12" y1="17" x2="12.01" y2="17" stroke="#000"/>
            </svg>
          </div>`,
    className: '',
    iconSize: [20, 20],
    iconAnchor: [10, 10]
  });

  L.marker([13.0622, 80.2484], { icon: alertIcon }).addTo(map);
  L.marker([13.04, 80.23], { icon: alertIcon }).addTo(map);
}
