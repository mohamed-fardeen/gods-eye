export function renderIncidents() {
  const alerts = [
    { title:'Accident Detected', loc:'Anna Salai Junction, T. Nagar', cam:'CAM-07', sev:'CRITICAL', time:'12:43 PM', type:'var(--red)' },
    { title:'Wrong-Way Vehicle', loc:'GST Road, Near Alandur Metro', cam:'CAM-12', sev:'HIGH', time:'12:37 PM', type:'var(--orange)' },
    { title:'Heavy Congestion', loc:'Mount Road, Egmore', cam:'CAM-23', sev:'HIGH', time:'12:32 PM', type:'var(--orange)' },
    { title:'Stopped Vehicle', loc:'OMR, Near Perungudi', cam:'CAM-08', sev:'MEDIUM', time:'12:30 PM', type:'var(--amber)' },
    { title:'Red Light Violation', loc:'Velachery Main Rd Junction', cam:'CAM-09', sev:'MEDIUM', time:'12:28 PM', type:'var(--amber)' },
    { title:'Overspeeding Detected', loc:'GST Road, Airport Side', cam:'CAM-42', sev:'HIGH', time:'12:24 PM', type:'var(--orange)' },
    { title:'Sudden Congestion', loc:'Adyar Bridge', cam:'CAM-15', sev:'MEDIUM', time:'12:20 PM', type:'var(--amber)' },
    { title:'Camera Offline', loc:'Kodambakkam Flyover', cam:'', sev:'INFO', time:'12:18 PM', type:'var(--blue)' },
  ];

  return `
    <div style="padding: 12px 16px; display: flex; flex-direction: column; gap: 12px; height: 100%; overflow-y: auto;">
      
      <!-- Top KPIs (In screenshot, these are placed at the top) -->
      <div style="display: flex; gap: 12px; margin-top: -12px;">
        <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 8px; padding: 10px 16px; display: flex; gap: 12px; align-items: center; min-width: 150px;">
          <div style="color:var(--red); display:flex; flex-direction:column; gap:4px;">
            <div style="display:flex; align-items:center; gap:6px; font-size:10px; font-weight:700; text-transform:uppercase;"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg> CRITICAL</div>
            <div style="font-size:20px; font-weight:800; color:#fff; line-height:1;">7</div>
          </div>
          <div style="display:flex; flex-direction:column; justify-content:flex-end; gap:4px; height:100%;">
            <div style="font-size:10px; color:var(--text-muted);">Active</div>
            <div style="font-size:9px; color:var(--text-dim); cursor:pointer;">View all</div>
          </div>
        </div>
        <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 8px; padding: 10px 16px; display: flex; gap: 12px; align-items: center; min-width: 150px;">
          <div style="color:var(--orange); display:flex; flex-direction:column; gap:4px;">
            <div style="display:flex; align-items:center; gap:6px; font-size:10px; font-weight:700; text-transform:uppercase;"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg> HIGH</div>
            <div style="font-size:20px; font-weight:800; color:#fff; line-height:1;">15</div>
          </div>
          <div style="display:flex; flex-direction:column; justify-content:flex-end; gap:4px; height:100%;">
            <div style="font-size:10px; color:var(--text-muted);">Active</div>
            <div style="font-size:9px; color:var(--text-dim); cursor:pointer;">View all</div>
          </div>
        </div>
        <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 8px; padding: 10px 16px; display: flex; gap: 12px; align-items: center; min-width: 150px;">
          <div style="color:var(--amber); display:flex; flex-direction:column; gap:4px;">
            <div style="display:flex; align-items:center; gap:6px; font-size:10px; font-weight:700; text-transform:uppercase;"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg> MEDIUM</div>
            <div style="font-size:20px; font-weight:800; color:#fff; line-height:1;">21</div>
          </div>
          <div style="display:flex; flex-direction:column; justify-content:flex-end; gap:4px; height:100%;">
            <div style="font-size:10px; color:var(--text-muted);">Active</div>
            <div style="font-size:9px; color:var(--text-dim); cursor:pointer;">View all</div>
          </div>
        </div>
        <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 8px; padding: 10px 16px; display: flex; gap: 12px; align-items: center; min-width: 150px;">
          <div style="color:var(--blue); display:flex; flex-direction:column; gap:4px;">
            <div style="display:flex; align-items:center; gap:6px; font-size:10px; font-weight:700; text-transform:uppercase;"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg> INFO</div>
            <div style="font-size:20px; font-weight:800; color:#fff; line-height:1;">12</div>
          </div>
          <div style="display:flex; flex-direction:column; justify-content:flex-end; gap:4px; height:100%;">
            <div style="font-size:10px; color:var(--text-muted);">Active</div>
            <div style="font-size:9px; color:var(--text-dim); cursor:pointer;">View all</div>
          </div>
        </div>
      </div>

      <!-- Main grid -->
      <div style="display: grid; grid-template-columns: 300px 1fr 340px; gap: 12px; flex: 1; min-height: 0;">
        
        <!-- Left: Alert List -->
        <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; display: flex; flex-direction: column; overflow: hidden;">
          <div style="padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">ALL ALERTS (55)</span>
            <div style="display:flex; gap:6px;">
              <select style="background:transparent; border:1px solid rgba(255,255,255,0.1); color:var(--text-200); font-size:9px; border-radius:4px; padding:4px;">
                <option>All Severity</option>
              </select>
              <select style="background:transparent; border:1px solid rgba(255,255,255,0.1); color:var(--text-200); font-size:9px; border-radius:4px; padding:4px;">
                <option>All Status</option>
              </select>
              <button style="background:transparent; border:1px solid rgba(255,255,255,0.1); color:var(--text-200); border-radius:4px; padding:4px; cursor:pointer;"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg></button>
            </div>
          </div>
          <div style="height: 100%; overflow-y: auto; padding: 12px;">
            ${alerts.map((a, i) => `
              <div style="padding:12px; border-radius:8px; display:flex; gap:12px; margin-bottom:8px; cursor:pointer; ${i===0 ? 'background:rgba(239,68,68,0.1); border:1px solid rgba(239,68,68,0.3);' : 'background:transparent; border:1px solid transparent; border-bottom:1px solid rgba(255,255,255,0.05);'}">
                <div style="color:${a.type}; margin-top:2px;">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
                </div>
                <div style="flex: 1; min-width: 0;">
                  <div style="font-size:12px; font-weight:600; color:${a.type}; margin-bottom:4px;">${a.title}</div>
                  <div style="font-size:10px; color:var(--text-200); margin-bottom:2px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${a.loc}</div>
                </div>
                <div style="display:flex; flex-direction:column; align-items:flex-end; gap:6px;">
                  <div style="font-size:10px; color:var(--text-dim);">${a.time}</div>
                  <div style="font-size:9px; color:${a.type}; font-weight:700; text-transform:uppercase;">${a.sev}</div>
                  <div style="font-size:9px; color:var(--text-muted);">${a.cam}</div>
                </div>
              </div>
            `).join('')}
          </div>
          <div style="padding: 12px 16px; border-top: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-between; align-items: center; font-size: 10px; color: var(--text-dim);">
            <span>Showing 1 to 8 of 55 alerts</span>
            <div style="display: flex; gap: 8px;">
              <span style="cursor:pointer;">&lsaquo;</span>
              <span style="background:var(--red); color:#fff; width:16px; height:16px; display:flex; align-items:center; justify-content:center; border-radius:4px; font-weight:700;">1</span>
              <span style="cursor:pointer;">2</span>
              <span style="cursor:pointer;">3</span>
              <span style="cursor:pointer;">4</span>
              <span style="cursor:pointer;">7</span>
              <span style="cursor:pointer;">&rsaquo;</span>
            </div>
          </div>
        </div>

        <!-- Middle: Alert Details -->
        <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; display: flex; flex-direction: column; overflow: hidden;">
          <div style="padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.05);">
            <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">ALERT DETAILS</span>
          </div>
          <div style="height: 100%; overflow-y: auto; padding: 20px;">
            <div style="display:flex; align-items:flex-start; justify-content:space-between; margin-bottom:16px;">
              <div style="display:flex; gap:12px; align-items:flex-start;">
                <div style="color:var(--red); margin-top:2px;">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
                </div>
                <div>
                  <h2 style="font-size:18px; font-weight:700; color:var(--red); margin:0 0 8px 0; display:flex; align-items:center; gap:12px;">
                    Accident Detected
                  </h2>
                  <div style="display:flex; flex-direction:column; gap:6px; font-size:11px; color:var(--text-200);">
                    <div style="display:flex; align-items:center; gap:8px;">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
                      Anna Salai Junction, T. Nagar, Chennai - 600017
                    </div>
                    <div style="display:flex; align-items:center; gap:8px;">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
                      Camera: CAM-07
                    </div>
                    <div style="display:flex; align-items:center; gap:8px;">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                      21 May 2024, 12:43:18 PM
                    </div>
                  </div>
                </div>
              </div>
              <div style="display:flex; gap:12px; align-items:center;">
                <span style="background:rgba(239,68,68,0.1); border:1px solid rgba(239,68,68,0.3); color:var(--red); font-size:10px; font-weight:700; padding:4px 8px; border-radius:4px; text-transform:uppercase;">CRITICAL</span>
                <span style="color:var(--text-muted); cursor:pointer;"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></span>
              </div>
            </div>
            <div style="display:flex; justify-content:flex-end; margin-top:-24px; margin-bottom:12px;">
              <span style="color:var(--red); font-size:11px; font-weight:700; display:flex; align-items:center; gap:4px;"><span style="width:6px; height:6px; border-radius:50%; background:var(--red); animation:ping 1.5s infinite;"></span> Live</span>
            </div>

            <!-- Tabs -->
            <div style="display:flex; border-bottom: 1px solid rgba(255,255,255,0.05); margin-bottom: 20px;">
              <div style="padding: 8px 16px; border-bottom: 2px solid var(--red); color: var(--red); font-size: 11px; font-weight: 700; text-transform: uppercase; cursor: pointer;">OVERVIEW</div>
              <div style="padding: 8px 16px; color: var(--text-muted); font-size: 11px; font-weight: 600; text-transform: uppercase; cursor: pointer;">VEHICLES (3)</div>
              <div style="padding: 8px 16px; color: var(--text-muted); font-size: 11px; font-weight: 600; text-transform: uppercase; cursor: pointer;">TIMELINE</div>
              <div style="padding: 8px 16px; color: var(--text-muted); font-size: 11px; font-weight: 600; text-transform: uppercase; cursor: pointer;">NOTES</div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 220px; gap: 24px; margin-bottom: 24px;">
              <!-- Info Col -->
              <div>
                <div style="font-size:11px; color:var(--text-dim); margin-bottom:6px;">Alert Description</div>
                <div style="font-size:12px; color:var(--text-200); line-height:1.5; margin-bottom:20px;">Possible accident detected. Vehicles are stopped on the road. Traffic movement severely affected.</div>
                
                <div style="font-size:11px; color:var(--text-dim); margin-bottom:8px;">AI Confidence</div>
                <div style="font-size:14px; font-weight:700; color:#fff; margin-bottom:4px;">94%</div>
                <div style="height:4px; background:rgba(255,255,255,0.1); border-radius:2px; margin-bottom:24px;">
                  <div style="width:94%; height:100%; background:var(--red); border-radius:2px;"></div>
                </div>

                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:y-16px; row-gap:16px;">
                  <div>
                    <div style="font-size:10px; color:var(--text-dim); margin-bottom:4px;">Severity</div>
                    <div style="font-size:12px; color:#fff;">Critical</div>
                  </div>
                  <div>
                    <div style="font-size:10px; color:var(--text-dim); margin-bottom:4px;">Impact</div>
                    <div style="font-size:12px; color:#fff;">High</div>
                  </div>
                  <div>
                    <div style="font-size:10px; color:var(--text-dim); margin-bottom:4px;">Traffic Impact</div>
                    <div style="font-size:12px; color:#fff;">Severe</div>
                  </div>
                  <div>
                    <div style="font-size:10px; color:var(--text-dim); margin-bottom:4px;">Detected By</div>
                    <div style="font-size:12px; color:#fff;">AI Detection</div>
                  </div>
                  <div>
                    <div style="font-size:10px; color:var(--text-dim); margin-bottom:4px;">Affected Lanes</div>
                    <div style="font-size:12px; color:#fff;">3 / 4</div>
                  </div>
                  <div>
                    <div style="font-size:10px; color:var(--text-dim); margin-bottom:4px;">Response Status</div>
                    <div style="font-size:12px; color:var(--text-200);">Pending</div>
                  </div>
                </div>
              </div>
              
              <!-- Map Col -->
              <div>
                <div style="font-size:11px; color:var(--text-dim); margin-bottom:6px;">Location on Map</div>
                <div style="width: 100%; height: 240px; background: #000; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); position: relative; overflow: hidden;" id="incident-minimap"></div>
              </div>
            </div>

            <div style="display: flex; gap: 12px; margin-bottom: 24px;">
              <button style="flex: 1.5; background: rgba(239,68,68,0.9); color: #fff; border: none; border-radius: 6px; padding: 10px; font-size: 12px; font-weight: 600; cursor: pointer; display: flex; justify-content: center; align-items: center; gap: 8px;">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg> Mark as Resolved
              </button>
              <button style="flex: 1; background: transparent; border: 1px solid rgba(255,255,255,0.1); color: #fff; border-radius: 6px; padding: 10px; font-size: 12px; font-weight: 600; cursor: pointer; display: flex; justify-content: center; align-items: center; gap: 8px;">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg> Share Alert
              </button>
            </div>

            <!-- Affected Vehicles -->
            <div>
              <div style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px; margin-bottom: 12px;">AFFECTED VEHICLES (3)</div>
              <table style="width: 100%; border-collapse: collapse; font-size: 10px;">
                <thead>
                  <tr style="color:var(--text-dim); border-bottom:1px solid rgba(255,255,255,0.05);">
                    <th style="text-align:left; padding-bottom:8px; font-weight:500;">#</th>
                    <th style="text-align:left; padding-bottom:8px; font-weight:500;">Type</th>
                    <th style="text-align:left; padding-bottom:8px; font-weight:500;">Plate Number</th>
                    <th style="text-align:left; padding-bottom:8px; font-weight:500;">Confidence</th>
                    <th style="text-align:left; padding-bottom:8px; font-weight:500;">Status</th>
                    <th style="text-align:left; padding-bottom:8px; font-weight:500;">First Detected</th>
                    <th style="text-align:left; padding-bottom:8px; font-weight:500;">Last Seen</th>
                    <th style="text-align:right; padding-bottom:8px; font-weight:500;">Speed</th>
                  </tr>
                </thead>
                <tbody style="color:var(--text-200);">
                  <tr style="border-bottom:1px solid rgba(255,255,255,0.03);">
                    <td style="padding: 8px 0; color:var(--text-muted);">1</td>
                    <td style="padding: 8px 0;"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="8" rx="2" ry="2"/><path d="M4 11V7a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v4"/><circle cx="7" cy="19" r="2"/><circle cx="17" cy="19" r="2"/></svg></td>
                    <td>TN09AB1234</td>
                    <td>96%</td>
                    <td><span style="background:rgba(239,68,68,0.1); color:var(--red); padding:2px 6px; border-radius:4px;">Involved</span></td>
                    <td>12:42:58 PM (CAM-07)</td>
                    <td>12:43:18 PM (CAM-07)</td>
                    <td style="text-align:right;">0 km/h</td>
                  </tr>
                  <tr style="border-bottom:1px solid rgba(255,255,255,0.03);">
                    <td style="padding: 8px 0; color:var(--text-muted);">2</td>
                    <td style="padding: 8px 0;"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="8" rx="2" ry="2"/><path d="M4 11V7a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v4"/><circle cx="7" cy="19" r="2"/><circle cx="17" cy="19" r="2"/></svg></td>
                    <td>TN11CD5678</td>
                    <td>94%</td>
                    <td><span style="background:rgba(239,68,68,0.1); color:var(--red); padding:2px 6px; border-radius:4px;">Involved</span></td>
                    <td>12:42:59 PM (CAM-07)</td>
                    <td>12:43:18 PM (CAM-07)</td>
                    <td style="text-align:right;">5 km/h</td>
                  </tr>
                  <tr>
                    <td style="padding: 8px 0; color:var(--text-muted);">3</td>
                    <td style="padding: 8px 0;"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="5" cy="18" r="4"/><circle cx="19" cy="18" r="4"/><path d="M12 17.5V14l-3-3 4-3 2 3h2"/></svg></td>
                    <td>TN07EF9012</td>
                    <td>92%</td>
                    <td><span style="background:rgba(239,68,68,0.1); color:var(--red); padding:2px 6px; border-radius:4px;">Involved</span></td>
                    <td>12:42:57 PM (CAM-07)</td>
                    <td>12:43:16 PM (CAM-07)</td>
                    <td style="text-align:right;">0 km/h</td>
                  </tr>
                </tbody>
              </table>
            </div>

          </div>
        </div>

        <!-- Right: Camera & Quick Actions -->
        <div style="display: flex; flex-direction: column; gap: 12px;">
          <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; overflow: hidden; display: flex; flex-direction: column;">
            <div style="padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-between; align-items: center;">
              <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">LIVE CAMERA - CAM-07</span>
              <div style="display:flex; align-items:center; gap:8px;">
                <span style="color:var(--red); font-size:10px; font-weight:700; display:flex; align-items:center; gap:4px;"><span style="width:6px; height:6px; border-radius:50%; background:var(--red);"></span> Live</span>
                <span style="color:var(--text-muted);"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/></svg></span>
              </div>
            </div>
            
            <div style="position: relative; width: 100%; height: 200px; background: url('https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?auto=format&fit=crop&q=80&w=600') center/cover;">
              <div style="position:absolute; inset:0; background:rgba(0,0,0,0.2);"></div>
              <!-- Simulated bounding boxes for cars -->
              <div style="position:absolute; bottom:20px; left:30%; width:30px; height:30px; border:1px solid var(--red); background:rgba(239,68,68,0.1);"></div>
              <div style="position:absolute; bottom:10px; right:40%; width:40px; height:40px; border:1px solid var(--red); background:rgba(239,68,68,0.1);"></div>
              
              <div style="position:absolute; bottom: 8px; left: 8px; background: rgba(0,0,0,0.6); color: #fff; font-size: 9px; padding: 4px 8px; border-radius: 4px;">21 May 2024 12:43:18 PM</div>
            </div>

            <div style="padding: 12px 16px;">
              <span style="font-size:9px; color:var(--text-dim); text-transform:uppercase; margin-bottom:8px; display:block;">AI DETECTIONS (Current Frame)</span>
              <div style="display: flex; justify-content: space-between;">
                <div style="display:flex; flex-direction:column; align-items:center; gap:4px;">
                  <div style="color:var(--red);"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="8" rx="2" ry="2"/><path d="M4 11V7a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v4"/><circle cx="7" cy="19" r="2"/><circle cx="17" cy="19" r="2"/></svg></div>
                  <div style="font-size:9px; color:var(--text-muted);">Cars</div>
                  <div style="font-size:14px; font-weight:700; color:#fff;">12</div>
                </div>
                <div style="display:flex; flex-direction:column; align-items:center; gap:4px;">
                  <div style="color:var(--amber);"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="5" cy="18" r="4"/><circle cx="19" cy="18" r="4"/><path d="M12 17.5V14l-3-3 4-3 2 3h2"/></svg></div>
                  <div style="font-size:9px; color:var(--text-muted);">Bikes</div>
                  <div style="font-size:14px; font-weight:700; color:#fff;">8</div>
                </div>
                <div style="display:flex; flex-direction:column; align-items:center; gap:4px;">
                  <div style="color:var(--blue);"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="6" width="20" height="12" rx="2" ry="2"/><circle cx="7" cy="18" r="2"/><circle cx="17" cy="18" r="2"/></svg></div>
                  <div style="font-size:9px; color:var(--text-muted);">Buses</div>
                  <div style="font-size:14px; font-weight:700; color:#fff;">2</div>
                </div>
                <div style="display:flex; flex-direction:column; align-items:center; gap:4px;">
                  <div style="color:var(--green);"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="14" height="10" rx="2" ry="2"/><rect x="16" y="11" width="6" height="6" rx="2" ry="2"/><circle cx="6" cy="17" r="2"/><circle cx="19" cy="17" r="2"/></svg></div>
                  <div style="font-size:9px; color:var(--text-muted);">Trucks</div>
                  <div style="font-size:14px; font-weight:700; color:#fff;">1</div>
                </div>
              </div>
            </div>
          </div>

          <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 12px 16px;">
            <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px; margin-bottom: 12px; display:block;">QUICK ACTIONS</span>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
              <button style="background: rgba(239,68,68,0.9); border: none; color: #fff; padding: 8px; border-radius: 6px; font-size: 11px; font-weight: 600; display:flex; align-items:center; justify-content:center; gap:6px; cursor:pointer;">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg> Notify Control Room
              </button>
              <button style="background: var(--blue); border: none; color: #fff; padding: 8px; border-radius: 6px; font-size: 11px; font-weight: 600; display:flex; align-items:center; justify-content:center; gap:6px; cursor:pointer;">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg> Dispatch Patrol
              </button>
              <button style="background: transparent; border: 1px solid rgba(255,255,255,0.1); color: #fff; padding: 8px; border-radius: 6px; font-size: 11px; font-weight: 600; display:flex; align-items:center; justify-content:center; gap:6px; cursor:pointer;">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg> Add Note
              </button>
              <button style="background: transparent; border: 1px solid rgba(255,255,255,0.1); color: #fff; padding: 8px; border-radius: 6px; font-size: 11px; font-weight: 600; display:flex; align-items:center; justify-content:center; gap:6px; cursor:pointer;">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg> Share Incident
              </button>
            </div>
          </div>

          <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 12px 16px; flex: 1;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
              <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">RECENT ALERTS NEARBY</span>
              <span style="font-size:10px; color:var(--blue); cursor:pointer;">View All</span>
            </div>
            
            <div style="display:flex; flex-direction:column; gap:12px;">
              <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div style="display:flex; gap:12px;">
                  <div style="color:var(--red);"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg></div>
                  <div>
                    <div style="font-size:12px; font-weight:600; color:var(--red);">Heavy Congestion</div>
                    <div style="font-size:10px; color:var(--text-200);">Anna Salai, Near T. Nagar Bus Stand</div>
                  </div>
                </div>
                <div style="display:flex; flex-direction:column; align-items:flex-end;">
                  <div style="font-size:10px; color:var(--text-dim);">12:39 PM</div>
                  <div style="font-size:9px; color:var(--text-muted);">CAM-06</div>
                </div>
              </div>
              <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div style="display:flex; gap:12px;">
                  <div style="color:var(--amber);"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg></div>
                  <div>
                    <div style="font-size:12px; font-weight:600; color:var(--amber);">Stopped Vehicle</div>
                    <div style="font-size:10px; color:var(--text-200);">Panagal Park Junction</div>
                  </div>
                </div>
                <div style="display:flex; flex-direction:column; align-items:flex-end;">
                  <div style="font-size:10px; color:var(--text-dim);">12:35 PM</div>
                  <div style="font-size:9px; color:var(--text-muted);">CAM-08</div>
                </div>
              </div>
              <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div style="display:flex; gap:12px;">
                  <div style="color:var(--amber);"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg></div>
                  <div>
                    <div style="font-size:12px; font-weight:600; color:var(--amber);">Red Light Violation</div>
                    <div style="font-size:10px; color:var(--text-200);">Bazullah Road Junction</div>
                  </div>
                </div>
                <div style="display:flex; flex-direction:column; align-items:flex-end;">
                  <div style="font-size:10px; color:var(--text-dim);">12:28 PM</div>
                  <div style="font-size:9px; color:var(--text-muted);">CAM-09</div>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>

    </div>
  `;
}

export function initIncidentsMap() {
  const mapContainer = document.getElementById('incident-minimap');
  if (!mapContainer || mapContainer._leaflet_id) return;
  
  const map = L.map('incident-minimap', {
    zoomControl: false,
    attributionControl: false,
    dragging: false,
    scrollWheelZoom: false,
    doubleClickZoom: false,
    boxZoom: false,
    keyboard: false
  }).setView([13.04, 80.24], 14); // Near Anna Salai Junction / T. Nagar
  
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    className: 'dark-map-tiles'
  }).addTo(map);

  const incidentIcon = L.divIcon({
    html: `<div style="color:var(--red); filter:drop-shadow(0 2px 4px rgba(0,0,0,0.5)); transform: translate(-50%, -100%); width: 24px; height: 32px; display:flex; justify-content:center;">
            <svg width="24" height="32" viewBox="0 0 24 32" fill="var(--red)">
              <path d="M12 0C5.373 0 0 5.373 0 12c0 9 12 20 12 20s12-11 12-20c0-6.627-5.373-12-12-12z" />
              <circle cx="12" cy="12" r="5" fill="#000" />
            </svg>
          </div>`,
    className: '',
    iconSize: [24, 32],
    iconAnchor: [12, 32]
  });

  L.marker([13.04, 80.24], { icon: incidentIcon }).addTo(map);

  // Add fake traffic lines near it
  L.polyline([[13.045, 80.235], [13.04, 80.24]], { color: 'var(--red)', weight: 3 }).addTo(map);
  L.polyline([[13.04, 80.24], [13.03, 80.245]], { color: 'var(--orange)', weight: 3 }).addTo(map);
}
