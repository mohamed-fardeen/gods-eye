export function renderCameraManagement() {
  const cameras = [
    { id:'CAM-01', loc:'Anna Salai Junction', zone:'Zone 1', status:'Online', health:98, hb:'2 sec ago', rec:true },
    { id:'CAM-02', loc:'T. Nagar Signal',     zone:'Zone 1', status:'Online', health:96, hb:'3 sec ago', rec:true },
    { id:'CAM-03', loc:'OMR Bridge',          zone:'Zone 2', status:'Online', health:95, hb:'1 sec ago', rec:true },
    { id:'CAM-04', loc:'Velachery Main Rd',   zone:'Zone 2', status:'Online', health:97, hb:'2 sec ago', rec:true },
    { id:'CAM-05', loc:'Guindy Signal',       zone:'Zone 2', status:'Online', health:94, hb:'2 sec ago', rec:true },
    { id:'CAM-06', loc:'Adyar Bridge',        zone:'Zone 2', status:'Online', health:93, hb:'4 sec ago', rec:true },
    { id:'CAM-07', loc:'Mount Road',          zone:'Zone 1', status:'Online', health:96, hb:'1 sec ago', rec:true, selected:true },
    { id:'CAM-08', loc:'GST Road',            zone:'Zone 3', status:'Offline', health:0,  hb:'3 min ago', rec:false },
    { id:'CAM-09', loc:'Perungudi Toll',      zone:'Zone 3', status:'Offline', health:0,  hb:'5 min ago', rec:false },
    { id:'CAM-10', loc:'ECR Road Junction',   zone:'Zone 3', status:'Maintenance', health:null, hb:'—', rec:false },
    { id:'CAM-11', loc:'Kodambakkam Flyover', zone:'Zone 1', status:'Online', health:93, hb:'1 sec ago', rec:true },
    { id:'CAM-12', loc:'Nungambakkam High Rd',zone:'Zone 1', status:'Online', health:95, hb:'2 sec ago', rec:true },
  ];

  return `
    <div style="padding: 24px; display: flex; flex-direction: column; gap: 20px; flex: 1; overflow-y: auto;">
      
      <!-- Top Title and KPIs -->
      <div style="display:flex; flex-direction:column; gap:16px;">
        <div>
          <h1 style="font-size:18px; font-weight:700; color:#fff; text-transform:uppercase; letter-spacing:0.5px; margin:0 0 4px 0;">CAMERA / INFRASTRUCTURE MANAGEMENT</h1>
          <div style="font-size:11px; color:var(--text-muted);">Monitor, configure and maintain the city camera network</div>
        </div>

        <div style="display:grid; grid-template-columns:repeat(6, 1fr); gap:12px;">
          <div style="background:rgba(12,17,32,0.9); border:1px solid rgba(255,255,255,0.07); border-radius:8px; padding:12px 16px; display:flex; justify-content:space-between; align-items:center;">
            <div>
              <div style="font-size:10px; color:var(--text-dim); text-transform:uppercase; font-weight:600; margin-bottom:4px;">TOTAL CAMERAS</div>
              <div style="font-size:20px; font-weight:700; color:#fff; line-height:1;">48</div>
              <div style="font-size:9px; color:var(--text-muted); margin-top:4px; display:flex; gap:6px; align-items:center;">
                <span style="color:var(--green); display:flex; align-items:center; gap:3px;"><span style="width:4px; height:4px; border-radius:50%; background:var(--green);"></span>42 Online</span>
                <span style="color:var(--text-muted); display:flex; align-items:center; gap:3px;"><span style="width:4px; height:4px; border-radius:50%; background:var(--text-muted);"></span>6 Offline</span>
              </div>
            </div>
            <div style="color:var(--blue);"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg></div>
          </div>
          
          <div style="background:rgba(12,17,32,0.9); border:1px solid rgba(255,255,255,0.07); border-radius:8px; padding:12px 16px; display:flex; justify-content:space-between; align-items:center;">
            <div>
              <div style="font-size:10px; color:var(--green); text-transform:uppercase; font-weight:600; margin-bottom:4px;">ONLINE</div>
              <div style="font-size:20px; font-weight:700; color:#fff; line-height:1;">42</div>
              <div style="font-size:9px; color:var(--green); margin-top:4px;">87.5%</div>
            </div>
            <div style="color:var(--green);"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg></div>
          </div>

          <div style="background:rgba(12,17,32,0.9); border:1px solid rgba(255,255,255,0.07); border-radius:8px; padding:12px 16px; display:flex; justify-content:space-between; align-items:center;">
            <div>
              <div style="font-size:10px; color:var(--red); text-transform:uppercase; font-weight:600; margin-bottom:4px;">OFFLINE</div>
              <div style="font-size:20px; font-weight:700; color:#fff; line-height:1;">6</div>
              <div style="font-size:9px; color:var(--red); margin-top:4px;">12.5%</div>
            </div>
            <div style="color:var(--red);"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m3 3 18 18M15 9.172a4 4 0 0 0-5.828 5.828"/><path d="M19.4 15.6C21.5 14.2 23 12 23 12c-2.3-4.5-6.5-7.5-11-7.5-1.4 0-2.8.3-4.1.8M3 12s2.3 4.5 6.5 7.5c2 1.4 4.3 2 6.5 2"/></svg></div>
          </div>

          <div style="background:rgba(12,17,32,0.9); border:1px solid rgba(255,255,255,0.07); border-radius:8px; padding:12px 16px; display:flex; justify-content:space-between; align-items:center;">
            <div>
              <div style="font-size:10px; color:var(--amber); text-transform:uppercase; font-weight:600; margin-bottom:4px;">MAINTENANCE</div>
              <div style="font-size:20px; font-weight:700; color:#fff; line-height:1;">2</div>
              <div style="font-size:9px; color:var(--amber); margin-top:4px;">4.2%</div>
            </div>
            <div style="color:var(--amber);"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg></div>
          </div>

          <div style="background:rgba(12,17,32,0.9); border:1px solid rgba(255,255,255,0.07); border-radius:8px; padding:12px 16px; display:flex; justify-content:space-between; align-items:center;">
            <div>
              <div style="font-size:10px; color:var(--purple); text-transform:uppercase; font-weight:600; margin-bottom:4px;">RECORDING</div>
              <div style="font-size:20px; font-weight:700; color:#fff; line-height:1;">40</div>
              <div style="font-size:9px; color:var(--purple); margin-top:4px;">83.3%</div>
            </div>
            <div style="color:var(--purple);"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="3"/></svg></div>
          </div>

          <div style="background:rgba(12,17,32,0.9); border:1px solid rgba(255,255,255,0.07); border-radius:8px; padding:12px 16px; display:flex; justify-content:space-between; align-items:center;">
            <div>
              <div style="font-size:10px; color:var(--cyan); text-transform:uppercase; font-weight:600; margin-bottom:4px;">TOTAL STORAGE</div>
              <div style="font-size:20px; font-weight:700; color:#fff; line-height:1;">18.6 TB</div>
              <div style="font-size:9px; color:var(--cyan); margin-top:4px;">12.4 TB Used</div>
            </div>
            <div style="color:var(--cyan);"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="2" width="20" height="8" rx="2" ry="2"/><rect x="2" y="14" width="20" height="8" rx="2" ry="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/></svg></div>
          </div>
        </div>
      </div>

      <div style="display:grid; grid-template-columns: 1fr 480px; gap:20px; flex:1; min-height:0;">
        
        <!-- Left Col -->
        <div style="display:flex; flex-direction:column; gap:20px; min-height:0;">
          
          <!-- Camera List -->
          <div style="background:rgba(12,17,32,0.9); border:1px solid rgba(255,255,255,0.07); border-radius:12px; display:flex; flex-direction:column; overflow:hidden;">
            <div style="padding:16px; border-bottom:1px solid rgba(255,255,255,0.05); display:flex; justify-content:space-between; align-items:center;">
              <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">CAMERA LIST</span>
              <div style="display:flex; gap:8px;">
                <div style="position:relative;">
                  <svg style="position:absolute; left:8px; top:5px; color:var(--text-muted);" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                  <input type="text" placeholder="Search by camera ID or location..." style="background:transparent; border:1px solid rgba(255,255,255,0.1); color:#fff; font-size:10px; border-radius:4px; padding:4px 8px 4px 24px; width:200px;">
                </div>
                <select style="background:transparent; border:1px solid rgba(255,255,255,0.1); color:var(--text-200); font-size:10px; border-radius:4px; padding:4px 8px;">
                  <option>All Status</option>
                </select>
                <select style="background:transparent; border:1px solid rgba(255,255,255,0.1); color:var(--text-200); font-size:10px; border-radius:4px; padding:4px 8px;">
                  <option>All Zones</option>
                </select>
                <button style="background:rgba(59,130,246,0.9); border:none; color:#fff; border-radius:4px; padding:4px 12px; font-size:10px; cursor:pointer; display:flex; align-items:center; gap:4px;"><svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg> Add Camera</button>
                <button style="background:transparent; border:1px solid rgba(255,255,255,0.1); color:var(--text-200); border-radius:4px; padding:4px; cursor:pointer;"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="1"/><circle cx="12" cy="5" r="1"/><circle cx="12" cy="19" r="1"/></svg></button>
              </div>
            </div>
            
            <div style="flex:1; overflow-y:auto;">
              <table style="width:100%; border-collapse:collapse; font-size:10px;">
                <thead>
                  <tr style="color:var(--text-dim); border-bottom:1px solid rgba(255,255,255,0.05); text-align:left;">
                    <th style="padding:10px 16px; font-weight:500;"><input type="checkbox" style="accent-color:var(--blue);"></th>
                    <th style="padding:10px 0; font-weight:500;">Camera ID</th>
                    <th style="padding:10px 0; font-weight:500;">Location</th>
                    <th style="padding:10px 0; font-weight:500;">Zone</th>
                    <th style="padding:10px 0; font-weight:500;">Status</th>
                    <th style="padding:10px 0; font-weight:500;">Health</th>
                    <th style="padding:10px 0; font-weight:500;">Last Heartbeat</th>
                    <th style="padding:10px 0; font-weight:500;">Recording</th>
                    <th style="padding:10px 16px; font-weight:500; text-align:right;">Actions</th>
                  </tr>
                </thead>
                <tbody style="color:var(--text-200);">
                  ${cameras.map(c => `
                    <tr style="border-bottom:1px solid rgba(255,255,255,0.03); ${c.selected ? 'background:rgba(59,130,246,0.1); border-left:2px solid var(--blue);' : 'border-left:2px solid transparent;'}">
                      <td style="padding:8px 16px;"><input type="checkbox" ${c.selected ? 'checked' : ''} style="accent-color:var(--blue);"></td>
                      <td style="padding:8px 0; display:flex; align-items:center; gap:6px;">
                        <span style="width:6px; height:6px; border-radius:50%; background:${c.status === 'Online' ? 'var(--blue)' : 'transparent'};"></span>
                        <span style="color:${c.selected ? '#fff' : 'var(--text-200)'}; font-weight:${c.selected ? '600' : '400'};">${c.id}</span>
                      </td>
                      <td style="padding:8px 0; color:${c.selected ? '#fff' : 'var(--text-200)'};">${c.loc}</td>
                      <td style="padding:8px 0;">${c.zone}</td>
                      <td style="padding:8px 0;">
                        <span style="color:${c.status==='Online'?'var(--green)':c.status==='Offline'?'var(--red)':'var(--amber)'}; display:flex; align-items:center; gap:4px;">
                          <span style="width:6px; height:6px; border-radius:50%; background:currentColor;"></span>${c.status}
                        </span>
                      </td>
                      <td style="padding:8px 0;">
                        ${c.health !== null ? `<div style="display:flex; align-items:center; gap:4px; color:${c.health > 90 ? 'var(--green)' : 'var(--red)'};"><svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg> ${c.health}%</div>` : '<span style="color:var(--text-muted);">—</span>'}
                      </td>
                      <td style="padding:8px 0;">${c.hb}</td>
                      <td style="padding:8px 0;">
                        ${c.rec ? `<span style="color:var(--red); font-size:9px; font-weight:700; display:flex; align-items:center; gap:4px;"><span style="width:6px; height:6px; border-radius:50%; background:var(--red);"></span> REC</span>` : '<span style="color:var(--text-muted);">—</span>'}
                      </td>
                      <td style="padding:8px 16px; text-align:right;">
                        <div style="display:flex; gap:8px; justify-content:flex-end;">
                          <span style="color:var(--text-muted); cursor:pointer;"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2" ry="2"/><path d="M12 8v8"/><path d="M8 12h8"/></svg></span>
                          <span style="color:var(--text-muted); cursor:pointer;"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg></span>
                          <span style="color:var(--text-muted); cursor:pointer;"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="1"/><circle cx="12" cy="5" r="1"/><circle cx="12" cy="19" r="1"/></svg></span>
                        </div>
                      </td>
                    </tr>
                  `).join('')}
                </tbody>
              </table>
            </div>
            
            <div style="padding:10px 16px; border-top:1px solid rgba(255,255,255,0.05); display:flex; justify-content:space-between; align-items:center; font-size:10px; color:var(--text-dim);">
              <span>Showing 1 to 12 of 48 cameras</span>
              <div style="display:flex; gap:6px;">
                <span style="cursor:pointer; color:var(--text-muted);">&lsaquo;</span>
                <span style="background:var(--blue); color:#fff; width:16px; height:16px; display:flex; align-items:center; justify-content:center; border-radius:4px;">1</span>
                <span style="cursor:pointer; color:var(--text-muted);">2</span>
                <span style="cursor:pointer; color:var(--text-muted);">3</span>
                <span style="cursor:pointer; color:var(--text-muted);">4</span>
                <span style="cursor:pointer; color:var(--text-muted);">&rsaquo;</span>
              </div>
            </div>
          </div>

          <!-- Camera Locations Map -->
          <div style="background:rgba(12,17,32,0.9); border:1px solid rgba(255,255,255,0.07); border-radius:12px; display:flex; flex-direction:column; overflow:hidden; flex:1;">
            <div style="padding:16px; border-bottom:1px solid rgba(255,255,255,0.05); position:absolute; z-index:2; width:100%; pointer-events:none;">
              <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">CAMERA LOCATIONS (48)</span>
            </div>
            <div id="cam-mgmt-minimap" style="width:100%; height:250px; background:#000;"></div>
            
            <!-- Floating legend -->
            <div style="position:absolute; bottom:30px; left:20px; background:rgba(8,12,20,0.8); border:1px solid rgba(255,255,255,0.1); border-radius:6px; padding:10px 12px; z-index:2;">
              <div style="display:flex; align-items:center; gap:8px; font-size:9px; color:var(--text-200); margin-bottom:6px;">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--green)" stroke-width="2"><circle cx="12" cy="12" r="7"/><circle cx="12" cy="12" r="10"/></svg> Online (42)
              </div>
              <div style="display:flex; align-items:center; gap:8px; font-size:9px; color:var(--text-200); margin-bottom:6px;">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--red)" stroke-width="2"><circle cx="12" cy="12" r="7"/><circle cx="12" cy="12" r="10"/></svg> Offline (6)
              </div>
              <div style="display:flex; align-items:center; gap:8px; font-size:9px; color:var(--text-200);">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--amber)" stroke-width="2"><circle cx="12" cy="12" r="7"/><circle cx="12" cy="12" r="10"/></svg> Maintenance (2)
              </div>
            </div>
          </div>
        </div>

        <!-- Right Col: Details -->
        <div style="background:rgba(12,17,32,0.9); border:1px solid rgba(255,255,255,0.07); border-radius:12px; display:flex; flex-direction:column; overflow:hidden;">
          
          <div style="padding:16px 20px; border-bottom:1px solid rgba(255,255,255,0.05); display:flex; justify-content:space-between; align-items:center;">
            <div style="display:flex; align-items:center; gap:8px;">
              <span style="font-size:12px; font-weight:700; color:var(--text-200);">CAM-07</span>
              <span style="font-size:14px; color:#fff;">Mount Road</span>
            </div>
            <div style="display:flex; align-items:center; gap:12px;">
              <span style="font-size:10px; color:var(--green); display:flex; align-items:center; gap:4px;"><span style="width:6px; height:6px; border-radius:50%; background:var(--green);"></span> Online</span>
              <span style="color:var(--text-muted); cursor:pointer;"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></span>
            </div>
          </div>
          
          <div style="display:flex; padding:0 20px; border-bottom: 1px solid rgba(255,255,255,0.05);">
            <div style="padding:10px 0; margin-right:24px; border-bottom:2px solid var(--blue); color:var(--blue); font-size:10px; font-weight:600; cursor:pointer;">Overview</div>
            <div style="padding:10px 0; margin-right:24px; color:var(--text-muted); font-size:10px; font-weight:500; cursor:pointer;">Configuration</div>
            <div style="padding:10px 0; margin-right:24px; color:var(--text-muted); font-size:10px; font-weight:500; cursor:pointer;">Maintenance</div>
            <div style="padding:10px 0; color:var(--text-muted); font-size:10px; font-weight:500; cursor:pointer;">Logs</div>
          </div>

          <div style="padding:20px; flex:1; overflow-y:auto; display:flex; flex-direction:column; gap:20px;">
            
            <!-- Video & FOV Map -->
            <div style="display:grid; grid-template-columns:1fr 140px; gap:12px;">
              <div style="position:relative; width:100%; height:140px; border-radius:6px; overflow:hidden; background:url('https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?auto=format&fit=crop&q=80&w=600') center/cover;">
                <div style="position:absolute; top:8px; left:8px; font-size:8px; color:#fff; background:rgba(0,0,0,0.6); padding:2px 6px; border-radius:4px;">21-05-2024 12:45:30</div>
                <div style="position:absolute; top:8px; right:8px; font-size:8px; color:#fff; background:rgba(34,197,94,0.8); padding:2px 6px; border-radius:4px; font-weight:700;">● LIVE</div>
                <div style="position:absolute; inset:0; background:rgba(0,0,0,0.2);"></div>
                <div style="position:absolute; bottom:20px; left:30%; width:30px; height:30px; border:1px solid var(--red); background:rgba(239,68,68,0.1);"></div>
                <div style="position:absolute; bottom:10px; right:40%; width:40px; height:40px; border:1px solid var(--red); background:rgba(239,68,68,0.1);"></div>
              </div>
              <div style="border-radius:6px; background:#000; overflow:hidden; border:1px solid rgba(255,255,255,0.1); position:relative;">
                <div style="position:absolute; inset:0; background:url('https://cartodb-basemaps-a.global.ssl.fastly.net/dark_all/15/23472/15312.png') center/cover; opacity:0.8;"></div>
                <!-- Triangle FOV representation -->
                <svg viewBox="0 0 100 100" style="position:absolute; inset:0; width:100%; height:100%;">
                  <polygon points="50,50 80,10 20,10" fill="rgba(59,130,246,0.2)" stroke="var(--blue)" stroke-width="1"/>
                  <circle cx="50" cy="50" r="4" fill="var(--blue)"/>
                </svg>
              </div>
            </div>

            <!-- Metadata Grid -->
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; font-size:10px;">
              <div style="display:flex; justify-content:space-between; border-bottom:1px solid rgba(255,255,255,0.03); padding-bottom:4px;">
                <span style="color:var(--text-dim);">Camera ID</span><span style="color:var(--text-200);">CAM-07</span>
              </div>
              <div style="display:flex; justify-content:space-between; border-bottom:1px solid rgba(255,255,255,0.03); padding-bottom:4px;">
                <span style="color:var(--text-dim);">Status</span><span style="color:var(--green);">Online</span>
              </div>
              <div style="display:flex; justify-content:space-between; border-bottom:1px solid rgba(255,255,255,0.03); padding-bottom:4px;">
                <span style="color:var(--text-dim);">Location</span><span style="color:var(--text-200);">Mount Road, Chennai</span>
              </div>
              <div style="display:flex; justify-content:space-between; border-bottom:1px solid rgba(255,255,255,0.03); padding-bottom:4px;">
                <span style="color:var(--text-dim);">IP Address</span><span style="color:var(--text-200);">10.10.1.27</span>
              </div>
              <div style="display:flex; justify-content:space-between; border-bottom:1px solid rgba(255,255,255,0.03); padding-bottom:4px;">
                <span style="color:var(--text-dim);">Zone</span><span style="color:var(--text-200);">Zone 1</span>
              </div>
              <div style="display:flex; justify-content:space-between; border-bottom:1px solid rgba(255,255,255,0.03); padding-bottom:4px;">
                <span style="color:var(--text-dim);">Resolution</span><span style="color:var(--text-200);">1920 × 1080 (1080p)</span>
              </div>
              <div style="display:flex; justify-content:space-between; border-bottom:1px solid rgba(255,255,255,0.03); padding-bottom:4px;">
                <span style="color:var(--text-dim);">Direction</span><span style="color:var(--text-200);">North-East</span>
              </div>
              <div style="display:flex; justify-content:space-between; border-bottom:1px solid rgba(255,255,255,0.03); padding-bottom:4px;">
                <span style="color:var(--text-dim);">FOV</span><span style="color:var(--text-200);">72°</span>
              </div>
              <div style="display:flex; justify-content:space-between; border-bottom:1px solid rgba(255,255,255,0.03); padding-bottom:4px;">
                <span style="color:var(--text-dim);">Latitude</span><span style="color:var(--text-200);">13.0622° N</span>
              </div>
              <div style="display:flex; justify-content:space-between; border-bottom:1px solid rgba(255,255,255,0.03); padding-bottom:4px;">
                <span style="color:var(--text-dim);">Codec</span><span style="color:var(--text-200);">H.265</span>
              </div>
              <div style="display:flex; justify-content:space-between; padding-bottom:4px;">
                <span style="color:var(--text-dim);">Longitude</span><span style="color:var(--text-200);">80.2484° E</span>
              </div>
              <div style="display:flex; justify-content:space-between; padding-bottom:4px;">
                <span style="color:var(--text-dim);">Installed On</span><span style="color:var(--text-200);">14-02-2024</span>
              </div>
            </div>

            <!-- 2x2 Grid Info -->
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
              <!-- Today's Summary -->
              <div style="border:1px solid rgba(255,255,255,0.05); border-radius:8px; padding:12px;">
                <div style="font-size:10px; font-weight:600; color:var(--text-muted); margin-bottom:12px;">Today's Summary</div>
                <div style="display:flex; justify-content:space-between; text-align:center;">
                  <div>
                    <div style="color:var(--orange); display:flex; justify-content:center;"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg></div>
                    <div style="font-size:8px; color:var(--text-dim); margin:4px 0 2px;">Vehicles</div>
                    <div style="font-size:12px; font-weight:700; color:#fff;">1,247</div>
                  </div>
                  <div>
                    <div style="color:var(--purple); display:flex; justify-content:center;"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg></div>
                    <div style="font-size:8px; color:var(--text-dim); margin:4px 0 2px;">ANPR Reads</div>
                    <div style="font-size:12px; font-weight:700; color:#fff;">842</div>
                  </div>
                  <div>
                    <div style="color:var(--red); display:flex; justify-content:center;"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/></svg></div>
                    <div style="font-size:8px; color:var(--text-dim); margin:4px 0 2px;">Incidents</div>
                    <div style="font-size:12px; font-weight:700; color:#fff;">3</div>
                  </div>
                  <div>
                    <div style="color:var(--green); display:flex; justify-content:center;"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg></div>
                    <div style="font-size:8px; color:var(--text-dim); margin:4px 0 2px;">Uptime</div>
                    <div style="font-size:12px; font-weight:700; color:#fff;">23h 45m</div>
                  </div>
                </div>
              </div>

              <!-- Storage Usage -->
              <div style="border:1px solid rgba(255,255,255,0.05); border-radius:8px; padding:12px; position:relative;">
                <div style="font-size:10px; font-weight:600; color:var(--text-muted); margin-bottom:12px;">Storage Usage</div>
                <div style="display:flex; align-items:center; gap:12px;">
                  <div style="position:relative; width:48px; height:48px;">
                    <svg viewBox="0 0 36 36" style="transform:rotate(-90deg); width:48px; height:48px;">
                      <circle cx="18" cy="18" r="15.915" fill="transparent" stroke="rgba(255,255,255,0.1)" stroke-width="4"></circle>
                      <circle cx="18" cy="18" r="15.915" fill="transparent" stroke="var(--blue)" stroke-width="4" stroke-dasharray="78, 22"></circle>
                    </svg>
                    <div style="position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center;">
                      <span style="font-size:12px; font-weight:700; color:#fff;">78%</span>
                      <span style="font-size:7px; color:var(--text-dim);">Used</span>
                    </div>
                  </div>
                  <div>
                    <div style="font-size:11px; color:#fff; font-weight:600;">12.4 TB / 18.6 TB</div>
                    <div style="font-size:9px; color:var(--text-dim); margin-top:2px;">Retention: 15 Days</div>
                    <button style="background:transparent; border:1px solid rgba(255,255,255,0.1); color:var(--blue); font-size:9px; padding:2px 8px; border-radius:4px; margin-top:8px; cursor:pointer;">Manage Storage</button>
                  </div>
                </div>
              </div>

              <!-- Recent Events -->
              <div style="border:1px solid rgba(255,255,255,0.05); border-radius:8px; padding:12px;">
                <div style="font-size:10px; font-weight:600; color:var(--text-muted); margin-bottom:12px;">Recent Events</div>
                <div style="display:flex; flex-direction:column; gap:8px;">
                  <div style="display:flex; gap:8px; align-items:flex-start;">
                    <div style="color:var(--green); margin-top:1px;"><svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><circle cx="12" cy="12" r="10"/></svg></div>
                    <div>
                      <div style="font-size:10px; color:var(--text-200);">Camera online</div>
                      <div style="font-size:8px; color:var(--text-dim);">21 May 2024, 12:45:28 PM</div>
                    </div>
                  </div>
                  <div style="display:flex; gap:8px; align-items:flex-start;">
                    <div style="color:var(--purple); margin-top:1px;"><svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><circle cx="12" cy="12" r="10"/></svg></div>
                    <div>
                      <div style="font-size:10px; color:var(--text-200);">Recording started</div>
                      <div style="font-size:8px; color:var(--text-dim);">21 May 2024, 12:45:25 PM</div>
                    </div>
                  </div>
                  <div style="display:flex; gap:8px; align-items:flex-start;">
                    <div style="color:var(--green); margin-top:1px;"><svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><circle cx="12" cy="12" r="10"/></svg></div>
                    <div>
                      <div style="font-size:10px; color:var(--text-200);">Configuration updated</div>
                      <div style="font-size:8px; color:var(--text-dim);">21 May 2024, 10:15:12 AM</div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- AI Health -->
              <div style="border:1px solid rgba(255,255,255,0.05); border-radius:8px; padding:12px;">
                <div style="font-size:10px; font-weight:600; color:var(--text-muted); margin-bottom:12px;">AI Health (Last 24h)</div>
                <div style="display:flex; flex-direction:column; gap:6px; font-size:10px;">
                  <div style="display:flex; justify-content:space-between;">
                    <span style="color:var(--text-200);">Detection Confidence</span>
                    <span style="color:var(--green); font-weight:600;">96% &uarr;</span>
                  </div>
                  <div style="display:flex; justify-content:space-between;">
                    <span style="color:var(--text-200);">ANPR Confidence</span>
                    <span style="color:var(--green); font-weight:600;">94% &uarr;</span>
                  </div>
                  <div style="display:flex; justify-content:space-between;">
                    <span style="color:var(--text-200);">False Positive Rate</span>
                    <span style="color:var(--green); font-weight:600;">2.1% &darr;</span>
                  </div>
                  <div style="display:flex; justify-content:space-between;">
                    <span style="color:var(--text-200);">Missed Detections</span>
                    <span style="color:var(--green); font-weight:600;">1.8% &darr;</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Footer Actions -->
            <div style="display:grid; grid-template-columns: 1fr 1fr 1fr 36px; gap:8px;">
              <button style="background:rgba(59,130,246,0.1); border:1px solid rgba(59,130,246,0.4); color:var(--blue); border-radius:6px; padding:10px; font-size:11px; font-weight:600; display:flex; justify-content:center; align-items:center; gap:6px; cursor:pointer;"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="5 3 19 12 5 21 5 3"/></svg> View Live</button>
              <button style="background:transparent; border:1px solid rgba(255,255,255,0.2); color:var(--text-200); border-radius:6px; padding:10px; font-size:11px; font-weight:600; display:flex; justify-content:center; align-items:center; gap:6px; cursor:pointer;"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="19 20 9 12 19 4 19 20"/><line x1="5" y1="19" x2="5" y2="5"/></svg> View Playback</button>
              <button style="background:rgba(239,68,68,0.9); border:none; color:#fff; border-radius:6px; padding:10px; font-size:11px; font-weight:600; display:flex; justify-content:center; align-items:center; gap:6px; cursor:pointer;"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/></svg> Restart Camera</button>
              <button style="background:transparent; border:1px solid rgba(255,255,255,0.2); color:var(--text-200); border-radius:6px; padding:10px; display:flex; justify-content:center; align-items:center; cursor:pointer;"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="1"/><circle cx="12" cy="5" r="1"/><circle cx="12" cy="19" r="1"/></svg></button>
            </div>
          </div>
        </div>

      </div>

    </div>
  `;
}

export function initCameraManagementMap() {
  const mapContainer = document.getElementById('cam-mgmt-minimap');
  if (!mapContainer || mapContainer._leaflet_id) return;
  
  const map = L.map('cam-mgmt-minimap', {
    zoomControl: true,
    attributionControl: false
  }).setView([13.06, 80.25], 12); 
  
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    className: 'dark-map-tiles'
  }).addTo(map);

  const createDotIcon = (color) => L.divIcon({
    html: `<div style="width: 12px; height: 12px; border-radius: 50%; background: ${color}; border: 2px solid rgba(12,17,32,0.9); filter: drop-shadow(0 0 4px ${color});"></div>`,
    className: '',
    iconSize: [12, 12],
    iconAnchor: [6, 6]
  });

  const greenIcon = createDotIcon('var(--green)');
  const redIcon = createDotIcon('var(--red)');
  const amberIcon = createDotIcon('var(--amber)');
  const selectedIcon = L.divIcon({
    html: `<div style="width: 16px; height: 16px; border-radius: 50%; background: var(--green); border: 2px solid #fff; filter: drop-shadow(0 0 6px var(--green)); position:relative;"><div style="position:absolute; inset:-8px; border-radius:50%; border:1px solid var(--green); animation: ping 1.5s infinite;"></div></div>`,
    className: '',
    iconSize: [16, 16],
    iconAnchor: [8, 8]
  });

  // Simulated points
  const points = [
    [13.0827, 80.2707, greenIcon],
    [13.0622, 80.2484, selectedIcon], // CAM-07 Mount Road
    [13.05, 80.23, greenIcon],
    [13.04, 80.24, greenIcon],
    [13.03, 80.21, amberIcon],
    [13.01, 80.22, redIcon],
    [12.98, 80.25, greenIcon],
    [12.99, 80.20, greenIcon],
    [13.00, 80.25, redIcon],
    [13.07, 80.22, greenIcon],
    [13.08, 80.23, amberIcon]
  ];

  points.forEach(([lat, lng, icon]) => {
    L.marker([lat, lng], { icon }).addTo(map);
  });
}
