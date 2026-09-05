export function renderPlateSearch() {
  return `
    <div style="padding: 12px 16px; display: flex; flex-direction: column; gap: 12px; height: 100%; overflow-y: auto;">
      
      <!-- Top Search Area -->
      <div style="display: flex; gap: 12px;">
        <!-- Search Input Box -->
        <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 20px; flex: 1; display: flex; flex-direction: column; gap: 12px;">
          
          <div style="display: flex; gap: 12px; align-items: flex-start;">
            <div style="flex: 1;">
              <div style="font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">ENTER NUMBER PLATE</div>
              <div style="display: flex; gap: 12px;">
                <div style="position: relative; flex: 1;">
                  <input type="text" value="TN09AB1234" style="width: 100%; background: rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 12px 16px; color: #fff; font-size: 16px; font-weight: 600; outline: none; letter-spacing: 1px;">
                  <div style="position: absolute; right: 16px; top: 50%; transform: translateY(-50%); color: var(--text-muted); cursor: pointer;"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></div>
                </div>
                <button style="background: var(--blue); border: none; border-radius: 8px; padding: 0 24px; color: #fff; font-size: 13px; font-weight: 600; display: flex; align-items: center; gap: 8px; cursor: pointer;">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg> SEARCH
                </button>
              </div>
            </div>
            
            <div style="width: 200px; padding-left: 20px; border-left: 1px solid rgba(255,255,255,0.07);">
              <div style="font-size: 11px; font-weight: 700; color: var(--blue); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">SEARCH TIPS</div>
              <div style="font-size: 11px; color: var(--text-200); line-height: 1.5;">Search with full plate number for best results.</div>
              <div style="font-size: 10px; color: var(--text-muted); margin-top: 4px;">Example: TN09AB1234</div>
            </div>
          </div>

          <!-- Search Result Summary -->
          <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.05);">
            <div>
              <div style="display: flex; align-items: center; gap: 6px; color: var(--green); margin-bottom: 4px;">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
                <span style="font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">PLATE FOUND</span>
              </div>
              <div style="font-size: 24px; font-weight: 800; color: #fff; letter-spacing: 1px;">TN09AB1234</div>
            </div>
            
            <div style="display: flex; gap: 32px;">
              <div style="display: flex; flex-direction: column; gap: 4px;">
                <span style="font-size: 10px; color: var(--text-muted);">Vehicle Type</span>
                <div style="display: flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 600; color: #fff;">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--blue)" stroke-width="2"><path d="M5 17H3a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v5h-3"/><path d="M14 17a2 2 0 1 0 4 0 2 2 0 0 0-4 0"/><path d="M5 17a2 2 0 1 0 4 0 2 2 0 0 0-4 0"/></svg> Sedan
                </div>
              </div>
              
              <div style="display: flex; flex-direction: column; gap: 4px;">
                <span style="font-size: 10px; color: var(--text-muted);">Vehicle Color</span>
                <div style="display: flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 600; color: #fff;">
                  <div style="width: 14px; height: 14px; border-radius: 50%; background: #fff; border: 1px solid rgba(255,255,255,0.2);"></div> White
                </div>
              </div>

              <div style="display: flex; flex-direction: column; gap: 4px;">
                <span style="font-size: 10px; color: var(--text-muted);">First Seen</span>
                <div style="display: flex; align-items: center; gap: 6px; font-size: 11px; font-weight: 600; color: #fff;">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--blue)" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg> 21 May 2024
                </div>
                <div style="font-size: 11px; color: var(--text-200); padding-left: 20px;">10:32:18 AM</div>
              </div>

              <div style="display: flex; flex-direction: column; gap: 4px;">
                <span style="font-size: 10px; color: var(--text-muted);">Last Seen</span>
                <div style="display: flex; align-items: center; gap: 6px; font-size: 11px; font-weight: 600; color: #fff;">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--blue)" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg> 21 May 2024
                </div>
                <div style="font-size: 11px; color: var(--text-200); padding-left: 20px;">12:43:52 PM</div>
              </div>

              <div style="display: flex; flex-direction: column; gap: 4px;">
                <span style="font-size: 10px; color: var(--text-muted);">Total Detections</span>
                <div style="display: flex; align-items: center; gap: 6px; font-size: 15px; font-weight: 700; color: var(--blue);">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg> 17
                </div>
                <div style="font-size: 10px; color: var(--text-200);">Across 7 Cameras</div>
              </div>
            </div>
            
          </div>
        </div>
      </div>

      <!-- 3 Column Main Content -->
      <div style="display: grid; grid-template-columns: 280px 1.5fr 1fr; gap: 12px; flex: 1; min-height: 500px;">
        
        <!-- Column 1: Detection Timeline -->
        <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; display: flex; flex-direction: column; overflow: hidden;">
          <div style="padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.05); background: rgba(0,0,0,0.2);">
            <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">DETECTION TIMELINE</span>
          </div>
          
          <div style="padding: 20px; height: 100%; overflow-y: auto; position: relative;">
            <!-- Timeline vertical line -->
            <div style="position: absolute; left: 31px; top: 30px; bottom: 30px; width: 2px; background: rgba(255,255,255,0.05); z-index: 1;"></div>
            
            <div style="display: flex; flex-direction: column; gap: 24px; position: relative; z-index: 2;">
              
              <!-- Timeline Item 1 -->
              <div style="display: flex; gap: 12px;">
                <div style="width: 24px; height: 24px; border-radius: 50%; background: var(--green); color: #000; font-size: 12px; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 0 0 4px rgba(12,17,32,1);">1</div>
                <div style="flex: 1; display: flex; gap: 12px;">
                  <div style="width: 60px; height: 40px; background: rgba(0,0,0,0.5); border-radius: 4px; border: 1px solid rgba(255,255,255,0.1);"></div>
                  <div style="flex: 1;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                      <div style="font-size: 11px; font-weight: 600; color: #fff;">10:32:18 AM</div>
                      <div style="background: rgba(34,197,94,0.1); border: 1px solid rgba(34,197,94,0.3); color: var(--green); font-size: 9px; font-weight: 600; padding: 2px 6px; border-radius: 4px;">Entry</div>
                    </div>
                    <div style="font-size: 10px; font-weight: 600; color: var(--text-200); margin-top: 2px;">CAM-03</div>
                    <div style="font-size: 10px; color: var(--text-muted); margin-top: 1px;">Anna Salai Junction</div>
                  </div>
                </div>
              </div>

              <!-- Timeline Item 2 -->
              <div style="display: flex; gap: 12px;">
                <div style="width: 24px; height: 24px; border-radius: 50%; background: #4ade80; color: #000; font-size: 12px; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 0 0 4px rgba(12,17,32,1);">2</div>
                <div style="flex: 1; display: flex; gap: 12px;">
                  <div style="width: 60px; height: 40px; background: rgba(0,0,0,0.5); border-radius: 4px; border: 1px solid rgba(255,255,255,0.1);"></div>
                  <div style="flex: 1;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                      <div style="font-size: 11px; font-weight: 600; color: #fff;">10:41:07 AM</div>
                      <div style="background: rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.3); color: var(--blue); font-size: 9px; font-weight: 600; padding: 2px 6px; border-radius: 4px;">Moving</div>
                    </div>
                    <div style="font-size: 10px; font-weight: 600; color: var(--text-200); margin-top: 2px;">CAM-05</div>
                    <div style="font-size: 10px; color: var(--text-muted); margin-top: 1px;">T. Nagar Signal</div>
                  </div>
                </div>
              </div>

              <!-- Timeline Item 3 -->
              <div style="display: flex; gap: 12px;">
                <div style="width: 24px; height: 24px; border-radius: 50%; background: #65a30d; color: #fff; font-size: 12px; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 0 0 4px rgba(12,17,32,1);">3</div>
                <div style="flex: 1; display: flex; gap: 12px;">
                  <div style="width: 60px; height: 40px; background: rgba(0,0,0,0.5); border-radius: 4px; border: 1px solid rgba(255,255,255,0.1);"></div>
                  <div style="flex: 1;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                      <div style="font-size: 11px; font-weight: 600; color: #fff;">11:02:33 AM</div>
                      <div style="background: rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.3); color: var(--blue); font-size: 9px; font-weight: 600; padding: 2px 6px; border-radius: 4px;">Moving</div>
                    </div>
                    <div style="font-size: 10px; font-weight: 600; color: var(--text-200); margin-top: 2px;">CAM-07</div>
                    <div style="font-size: 10px; color: var(--text-muted); margin-top: 1px;">Guindy Signal</div>
                  </div>
                </div>
              </div>
              
              <!-- Timeline Item 4 -->
              <div style="display: flex; gap: 12px;">
                <div style="width: 24px; height: 24px; border-radius: 50%; background: #84cc16; color: #000; font-size: 12px; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 0 0 4px rgba(12,17,32,1);">4</div>
                <div style="flex: 1; display: flex; gap: 12px;">
                  <div style="width: 60px; height: 40px; background: rgba(0,0,0,0.5); border-radius: 4px; border: 1px solid rgba(255,255,255,0.1);"></div>
                  <div style="flex: 1;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                      <div style="font-size: 11px; font-weight: 600; color: #fff;">11:37:21 AM</div>
                      <div style="background: rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.3); color: var(--blue); font-size: 9px; font-weight: 600; padding: 2px 6px; border-radius: 4px;">Moving</div>
                    </div>
                    <div style="font-size: 10px; font-weight: 600; color: var(--text-200); margin-top: 2px;">CAM-11</div>
                    <div style="font-size: 10px; color: var(--text-muted); margin-top: 1px;">Adyar Bridge</div>
                  </div>
                </div>
              </div>
              
              <!-- Timeline Item 5 -->
              <div style="display: flex; gap: 12px;">
                <div style="width: 24px; height: 24px; border-radius: 50%; background: #a3e635; color: #000; font-size: 12px; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 0 0 4px rgba(12,17,32,1);">5</div>
                <div style="flex: 1; display: flex; gap: 12px;">
                  <div style="width: 60px; height: 40px; background: rgba(0,0,0,0.5); border-radius: 4px; border: 1px solid rgba(255,255,255,0.1);"></div>
                  <div style="flex: 1;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                      <div style="font-size: 11px; font-weight: 600; color: #fff;">12:05:44 PM</div>
                      <div style="background: rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.3); color: var(--blue); font-size: 9px; font-weight: 600; padding: 2px 6px; border-radius: 4px;">Moving</div>
                    </div>
                    <div style="font-size: 10px; font-weight: 600; color: var(--text-200); margin-top: 2px;">CAM-15</div>
                    <div style="font-size: 10px; color: var(--text-muted); margin-top: 1px;">Thiruvanmiyur Junction</div>
                  </div>
                </div>
              </div>
              
              <!-- Timeline Item 6 -->
              <div style="display: flex; gap: 12px;">
                <div style="width: 24px; height: 24px; border-radius: 50%; background: #d9f99d; color: #000; font-size: 12px; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 0 0 4px rgba(12,17,32,1);">6</div>
                <div style="flex: 1; display: flex; gap: 12px;">
                  <div style="width: 60px; height: 40px; background: rgba(0,0,0,0.5); border-radius: 4px; border: 1px solid rgba(255,255,255,0.1);"></div>
                  <div style="flex: 1;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                      <div style="font-size: 11px; font-weight: 600; color: #fff;">12:26:10 PM</div>
                      <div style="background: rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.3); color: var(--blue); font-size: 9px; font-weight: 600; padding: 2px 6px; border-radius: 4px;">Moving</div>
                    </div>
                    <div style="font-size: 10px; font-weight: 600; color: var(--text-200); margin-top: 2px;">CAM-18</div>
                    <div style="font-size: 10px; color: var(--text-muted); margin-top: 1px;">ECR Road Junction</div>
                  </div>
                </div>
              </div>
              
              <!-- Timeline Item 7 -->
              <div style="display: flex; gap: 12px;">
                <div style="width: 24px; height: 24px; border-radius: 50%; background: var(--red); color: #fff; font-size: 12px; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 0 0 4px rgba(12,17,32,1);">7</div>
                <div style="flex: 1; display: flex; gap: 12px;">
                  <div style="width: 60px; height: 40px; background: rgba(0,0,0,0.5); border-radius: 4px; border: 1px solid rgba(255,255,255,0.1);"></div>
                  <div style="flex: 1;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                      <div style="font-size: 11px; font-weight: 600; color: #fff;">12:43:52 PM</div>
                      <div style="background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); color: var(--red); font-size: 9px; font-weight: 600; padding: 2px 6px; border-radius: 4px;">Exit</div>
                    </div>
                    <div style="font-size: 10px; font-weight: 600; color: var(--text-200); margin-top: 2px;">CAM-21</div>
                    <div style="font-size: 10px; color: var(--text-muted); margin-top: 1px;">Besant Nagar Beach Rd</div>
                  </div>
                </div>
              </div>

            </div>
          </div>
        </div>

        <!-- Column 2: Map View -->
        <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; display: flex; flex-direction: column; overflow: hidden; position: relative; z-index: 1;">
          <div style="padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-between; align-items: center; background: rgba(0,0,0,0.2); position:relative; z-index:10;">
            <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">VEHICLE MOVEMENT PATH</span>
            <div style="display:flex; align-items:center; gap:8px;">
              <div style="width:24px; height:12px; background:rgba(255,255,255,0.2); border-radius:6px; position:relative; cursor:pointer;">
                <div style="width:10px; height:10px; background:#fff; border-radius:50%; position:absolute; left:1px; top:1px;"></div>
              </div>
              <span style="font-size:10px; color:var(--text-muted);">Show Heatmap</span>
            </div>
          </div>
          
          <div id="platesearch-map" style="flex: 1; min-height: 0; background: #000; position: relative; border-bottom-left-radius: 12px; border-bottom-right-radius: 12px; z-index: 1;">
            <!-- Leaflet map goes here -->
          </div>

          <!-- Map Legend Overlay -->
          <div style="position: absolute; bottom: 16px; left: 16px; background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 8px; padding: 8px 12px; display: flex; gap: 12px; align-items: center; z-index: 1000;">
            <div style="display:flex; align-items:center; gap:6px;"><div style="width:8px; height:8px; border-radius:50%; background:var(--green);"></div><span style="font-size:10px; color:var(--text-200);">Entry</span></div>
            <div style="display:flex; align-items:center; gap:6px;"><div style="width:8px; height:8px; border-radius:50%; background:var(--amber);"></div><span style="font-size:10px; color:var(--text-200);">Moving</span></div>
            <div style="display:flex; align-items:center; gap:6px;"><div style="width:8px; height:8px; border-radius:50%; background:var(--red);"></div><span style="font-size:10px; color:var(--text-200);">Exit</span></div>
            <div style="display:flex; align-items:center; gap:6px; margin-left:8px;"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg><span style="font-size:10px; color:var(--text-200);">Cameras</span></div>
          </div>
        </div>

        <!-- Column 3: Summary & Stats -->
        <div style="display: flex; flex-direction: column; gap: 12px; overflow-y: auto;">
          
          <!-- Vehicle Summary -->
          <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 12px 16px;">
            <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px; margin-bottom: 12px; display:block;">VEHICLE SUMMARY</span>
            <div style="display: flex; gap: 12px;">
              <div style="width: 100px; height: 75px; background: rgba(0,0,0,0.5); border-radius: 6px; border: 1px solid rgba(255,255,255,0.1);"></div>
              <div style="flex: 1; display: flex; flex-direction: column; gap: 4px;">
                <div style="display:flex; justify-content:space-between; font-size:10px;"><span style="color:var(--text-dim);">Plate Number</span><span style="font-weight:700; color:#fff;">TN09AB1234</span></div>
                <div style="display:flex; justify-content:space-between; font-size:10px;"><span style="color:var(--text-dim);">Vehicle Type</span><span style="color:#fff;">Sedan</span></div>
                <div style="display:flex; justify-content:space-between; font-size:10px;"><span style="color:var(--text-dim);">Vehicle Color</span><span style="color:#fff;">White</span></div>
                <div style="display:flex; justify-content:space-between; font-size:10px;"><span style="color:var(--text-dim);">Make</span><span style="color:#fff;">Honda</span></div>
                <div style="display:flex; justify-content:space-between; font-size:10px;"><span style="color:var(--text-dim);">Model</span><span style="color:#fff;">City</span></div>
                <div style="display:flex; justify-content:space-between; font-size:10px;"><span style="color:var(--text-dim);">Confidence</span><span style="color:#fff;">96%</span></div>
              </div>
            </div>
          </div>

          <!-- Detection Statistics -->
          <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 12px 16px;">
            <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px; margin-bottom: 12px; display:block;">DETECTION STATISTICS</span>
            <div style="display: flex; justify-content: space-between;">
              <div style="display:flex; flex-direction:column; align-items:center; gap:4px;">
                <div style="color:var(--blue);"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 17H3a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v5h-3"/><path d="M14 17a2 2 0 1 0 4 0 2 2 0 0 0-4 0"/><path d="M5 17a2 2 0 1 0 4 0 2 2 0 0 0-4 0"/></svg></div>
                <div style="font-size:13px; font-weight:700; color:#fff;">17</div>
                <div style="font-size:9px; color:var(--text-dim);">Detections</div>
              </div>
              <div style="display:flex; flex-direction:column; align-items:center; gap:4px;">
                <div style="color:var(--blue);"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg></div>
                <div style="font-size:13px; font-weight:700; color:#fff;">7</div>
                <div style="font-size:9px; color:var(--text-dim);">Cameras</div>
              </div>
              <div style="display:flex; flex-direction:column; align-items:center; gap:4px;">
                <div style="color:var(--blue);"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg></div>
                <div style="font-size:13px; font-weight:700; color:#fff;">2h 11m</div>
                <div style="font-size:9px; color:var(--text-dim);">Total Time</div>
              </div>
              <div style="display:flex; flex-direction:column; align-items:center; gap:4px;">
                <div style="color:var(--blue);"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s-8-4.5-8-11.8A8 8 0 0 1 12 2a8 8 0 0 1 8 8.2c0 7.3-8 11.8-8 11.8z"/><circle cx="12" cy="10" r="3"/></svg></div>
                <div style="font-size:13px; font-weight:700; color:#fff;">28.4 km</div>
                <div style="font-size:9px; color:var(--text-dim);">Distance Covered</div>
              </div>
            </div>
          </div>

          <!-- Plate Readings (ANPR) -->
          <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 12px 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
              <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">PLATE READINGS (ANPR)</span>
              <span style="font-size:10px; color:var(--blue); cursor:pointer;">View All</span>
            </div>
            <table style="width: 100%; border-collapse: collapse; font-size: 10px;">
              <thead>
                <tr style="color:var(--text-dim); border-bottom:1px solid rgba(255,255,255,0.05);">
                  <th style="text-align:left; padding-bottom:6px; font-weight:500;">Camera</th>
                  <th style="text-align:left; padding-bottom:6px; font-weight:500;">Time</th>
                  <th style="text-align:left; padding-bottom:6px; font-weight:500;">Plate</th>
                  <th style="text-align:right; padding-bottom:6px; font-weight:500;">Confidence</th>
                </tr>
              </thead>
              <tbody style="color:var(--text-200);">
                <tr><td style="padding: 6px 0;">CAM-03</td><td>10:32:18 AM</td><td style="color:#fff;">TN09AB1234</td><td style="text-align:right;">97%</td></tr>
                <tr><td style="padding: 6px 0;">CAM-05</td><td>10:41:07 AM</td><td style="color:#fff;">TN09AB1234</td><td style="text-align:right;">96%</td></tr>
                <tr><td style="padding: 6px 0;">CAM-07</td><td>11:02:33 AM</td><td style="color:#fff;">TN09AB1234</td><td style="text-align:right;">95%</td></tr>
                <tr><td style="padding: 6px 0;">CAM-11</td><td>11:37:21 AM</td><td style="color:#fff;">TN09AB1234</td><td style="text-align:right;">96%</td></tr>
                <tr><td style="padding: 6px 0;">CAM-15</td><td>12:05:44 PM</td><td style="color:#fff;">TN09AB1234</td><td style="text-align:right;">95%</td></tr>
                <tr><td style="padding: 6px 0; color:var(--text-muted);">...</td><td></td><td></td><td></td></tr>
              </tbody>
            </table>
          </div>

          <!-- Vehicle Snapshots -->
          <div style="background: rgba(12,17,32,0.9); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 12px 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
              <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">VEHICLE SNAPSHOTS</span>
              <span style="font-size:10px; color:var(--blue); cursor:pointer;">View All</span>
            </div>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px;">
              <div style="display:flex; flex-direction:column; gap:4px; align-items:center;">
                <div style="width:100%; aspect-ratio:4/3; background:rgba(0,0,0,0.5); border:1px solid rgba(255,255,255,0.1); border-radius:4px;"></div>
                <div style="font-size:9px; color:var(--text-200); text-align:center;">10:32:18 AM<br><span style="color:var(--text-muted);">CAM-03</span></div>
              </div>
              <div style="display:flex; flex-direction:column; gap:4px; align-items:center;">
                <div style="width:100%; aspect-ratio:4/3; background:rgba(0,0,0,0.5); border:1px solid rgba(255,255,255,0.1); border-radius:4px;"></div>
                <div style="font-size:9px; color:var(--text-200); text-align:center;">11:02:33 AM<br><span style="color:var(--text-muted);">CAM-07</span></div>
              </div>
              <div style="display:flex; flex-direction:column; gap:4px; align-items:center;">
                <div style="width:100%; aspect-ratio:4/3; background:rgba(0,0,0,0.5); border:1px solid rgba(255,255,255,0.1); border-radius:4px;"></div>
                <div style="font-size:9px; color:var(--text-200); text-align:center;">11:37:21 AM<br><span style="color:var(--text-muted);">CAM-11</span></div>
              </div>
              <div style="display:flex; flex-direction:column; gap:4px; align-items:center;">
                <div style="width:100%; aspect-ratio:4/3; background:rgba(0,0,0,0.5); border:1px solid rgba(255,255,255,0.1); border-radius:4px;"></div>
                <div style="font-size:9px; color:var(--text-200); text-align:center;">12:43:52 PM<br><span style="color:var(--text-muted);">CAM-21</span></div>
              </div>
            </div>
          </div>

        </div>
      </div>
      
      <div style="display:flex; align-items:center; gap:6px; color:var(--blue); font-size:11px;">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
        <span style="color:var(--text-muted);">Note: Times are in IST (UTC +5:30). Data is updated in real-time.</span>
      </div>

    </div>
  `;
}

export function initPlateSearchMap() {
  const mapContainer = document.getElementById('platesearch-map');
  if (!mapContainer || mapContainer._leaflet_id) return;
  
  const map = L.map('platesearch-map', {
    zoomControl: false,
    attributionControl: false
  }).setView([13.02, 80.24], 12);
  
  // Use standard OpenStreetMap tiles with dark CSS filter
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    className: 'dark-map-tiles'
  }).addTo(map);

  L.control.zoom({ position: 'topright' }).addTo(map);

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
  
  L.polyline(pathCoordinates, { color: '#f59e0b', weight: 4, dashArray: '8, 8' }).addTo(map);
  
  // Add markers with numbers
  const colors = [
    'var(--green)', '#4ade80', '#65a30d', '#84cc16', '#a3e635', '#d9f99d', 'var(--red)'
  ];
  
  pathCoordinates.forEach((coord, i) => {
    const icon = L.divIcon({
      html: `<div style="width:20px; height:20px; border-radius:50%; background:${colors[i]}; color:${i===0||i===2||i===6 ? '#fff':'#00'}; font-size:10px; font-weight:700; display:flex; align-items:center; justify-content:center; box-shadow:0 0 0 3px rgba(12,17,32,0.8);">${i+1}</div>`,
      className: '',
      iconSize: [20, 20],
      iconAnchor: [10, 10]
    });
    L.marker(coord, { icon }).addTo(map);
  });
}
