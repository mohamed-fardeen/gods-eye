export function renderSidebar() {
  const sidebar = document.getElementById('sidebar');
  sidebar.style.width = '240px';
  sidebar.style.background = '#080c14'; // Very dark
  sidebar.style.borderRight = '1px solid rgba(255,255,255,0.07)';
  sidebar.style.display = 'flex';
  sidebar.style.flexDirection = 'column';
  sidebar.style.height = '100%';

  sidebar.innerHTML = `
    <!-- Top Logo Area -->
    <div style="height: 70px; display:flex; align-items:center; gap: 12px; padding: 0 20px; border-bottom: 1px solid rgba(255,255,255,0.07); flex-shrink:0;">
      <div style="color:var(--cyan); filter:drop-shadow(0 0 4px rgba(34,211,238,0.5)); display:flex;">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
        </svg>
      </div>
      <div>
        <h1 style="font-size:16px; font-weight:800; letter-spacing:1px; color:#fff; line-height:1;">GOD'S EYE</h1>
        <p style="font-size:9px; color:var(--text-muted); margin-top:3px;">Chennai Traffic Command Center</p>
      </div>
    </div>

    <!-- Navigation Links -->
    <div class="sb-nav" style="padding:16px 12px; flex:1; overflow-y:auto; display:flex; flex-direction:column; gap:4px;">
      <a class="nav-item active" href="#/" data-path="#/" style="padding: 12px 16px; border-radius:8px;">
        <svg class="nav-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
        Dashboard
      </a>
      <a class="nav-item" href="#/map" data-path="#/map" style="padding: 12px 16px; border-radius:8px;">
        <svg class="nav-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
        Digital Twin
      </a>
      <a class="nav-item" href="#/cameras" data-path="#/cameras" style="padding: 12px 16px; border-radius:8px;">
        <svg class="nav-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
        Live Cameras
      </a>
      <a class="nav-item" href="#/plate-search" data-path="#/plate-search" style="padding: 12px 16px; border-radius:8px;">
        <svg class="nav-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        Plate Search
      </a>
      <a class="nav-item" href="#/vehicle-profile" data-path="#/vehicle-profile" style="padding: 12px 16px; border-radius:8px;">
        <svg class="nav-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 17H3a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v5h-3"/><path d="M14 17a2 2 0 1 0 4 0 2 2 0 0 0-4 0"/><path d="M5 17a2 2 0 1 0 4 0 2 2 0 0 0-4 0"/></svg>
        Vehicle Profile
      </a>
      <a class="nav-item" href="#/traffic" data-path="#/traffic" style="padding: 12px 16px; border-radius:8px;">
        <svg class="nav-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
        Traffic Analysis
      </a>
      <a class="nav-item" href="#/incidents" data-path="#/incidents" style="padding: 12px 16px; border-radius:8px;">
        <svg class="nav-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/></svg>
        Alerts & Incidents
      </a>
      <a class="nav-item" href="#/camera-management" data-path="#/camera-management" style="padding: 12px 16px; border-radius:8px;">
        <svg class="nav-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>
        Camera Management
      </a>
      <a class="nav-item" href="#/reports" data-path="#/reports" style="padding: 12px 16px; border-radius:8px;">
        <svg class="nav-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        Reports
      </a>
      <a class="nav-item" href="#/settings" data-path="#/settings" style="padding: 12px 16px; border-radius:8px;">
        <svg class="nav-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
        System Settings
      </a>
      <a class="nav-item" href="#/ocrtest" data-path="#/ocrtest" style="padding: 12px 16px; border-radius:8px;">
        <svg class="nav-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
        AI Worker Test
      </a>
    </div>

    <!-- Bottom Skyline Graphic Area -->
    <div style="position:relative; height: 180px; flex-shrink:0; border-top: 1px solid rgba(255,255,255,0.07); overflow:hidden; background:linear-gradient(to top, rgba(12,17,32,1) 0%, transparent 100%);">
      <!-- Simulated skyline SVG -->
      <svg style="position:absolute; bottom:0; left:0; width:100%; opacity:0.15; color:var(--cyan);" viewBox="0 0 200 100" preserveAspectRatio="none">
        <path d="M0 100 L0 80 L10 80 L10 60 L15 60 L15 40 L20 40 L20 70 L25 70 L25 90 L35 90 L35 30 L40 30 L40 20 L45 20 L45 50 L55 50 L55 80 L65 80 L65 60 L75 60 L75 45 L85 45 L85 85 L95 85 L95 25 L100 25 L100 15 L105 15 L105 40 L115 40 L115 75 L125 75 L125 55 L135 55 L135 85 L145 85 L145 65 L155 65 L155 35 L160 35 L160 20 L165 20 L165 50 L175 50 L175 80 L185 80 L185 60 L195 60 L195 90 L200 90 L200 100 Z" fill="currentColor"/>
      </svg>
      <div style="position:absolute; bottom:16px; left:20px; z-index:2; display:flex; flex-direction:column; gap:8px;">
        <div style="font-size:11px; font-weight:600; color:var(--text-100);">System Status</div>
        <div style="display:flex; align-items:center; gap:6px; font-size:10px; color:var(--green);">
          <div style="width:6px; height:6px; border-radius:50%; background:var(--green);"></div> All Systems Operational
        </div>
        <div style="display:flex; align-items:center; gap:6px; font-size:10px; color:var(--text-200);">
          <div style="width:6px; height:6px; border-radius:50%; background:var(--text-dim);"></div> Data Updated: 12:45:30 PM
        </div>
      </div>
    </div>
  `;
}

export function updateSidebarActive(hash) {
  document.querySelectorAll('.nav-item').forEach(item => {
    if (item.getAttribute('data-path') === hash) {
      item.classList.add('active');
    } else {
      item.classList.remove('active');
    }
  });
}
