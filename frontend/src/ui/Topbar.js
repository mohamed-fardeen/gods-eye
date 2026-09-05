export function renderTopbar() {
  const topbar = document.getElementById('topbar');
  topbar.style.height = '70px';
  topbar.style.background = 'transparent'; // No background, let the main area background show through
  topbar.style.borderBottom = '1px solid rgba(255,255,255,0.07)';
  topbar.style.display = 'flex';
  topbar.style.alignItems = 'center';
  topbar.style.justifyContent = 'space-between';
  topbar.style.padding = '0 24px';
  topbar.style.flexShrink = '0';
  topbar.style.zIndex = '100';

  topbar.innerHTML = `
    <!-- Left Area (Dynamic Title) -->
    <div id="tb-title-area" style="display:flex; flex-direction:column; gap:4px;">
      <h2 id="tb-title" style="font-size:18px; font-weight:800; color:#fff; letter-spacing:0.5px; text-transform:uppercase; line-height:1;">COMMAND DASHBOARD</h2>
      <p id="tb-subtitle" style="font-size:11px; color:var(--text-muted);">Real-time overview of city traffic and incidents</p>
    </div>
    
    <!-- Right Area (Weather, Time, Operator) -->
    <div style="display:flex; align-items:center; gap:24px; height: 100%;">
      <!-- Weather -->
      <div style="display:flex; align-items:center; gap:8px;">
        <div style="color:var(--amber);"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg></div>
        <div>
          <div style="font-size:14px; font-weight:700; color:#fff;">32°C</div>
        </div>
      </div>
      <div style="width:1px; height:24px; background:rgba(255,255,255,0.07);"></div>
      
      <!-- Date -->
      <div style="display:flex; align-items:center; gap:8px;">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
        <span style="font-size:12px; font-weight:600; color:#fff;">21 May 2024</span>
      </div>
      <div style="width:1px; height:24px; background:rgba(255,255,255,0.07);"></div>
      
      <!-- Time -->
      <div style="display:flex; align-items:center; gap:8px;">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        <span style="font-size:12px; font-weight:600; color:#fff;">12:45:30 PM</span>
      </div>
      <div style="width:1px; height:24px; background:rgba(255,255,255,0.07);"></div>
      
      <!-- Operator -->
      <div style="display:flex; align-items:center; gap:10px; cursor:pointer;">
        <div style="width:32px; height:32px; border-radius:50%; background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); display:flex; align-items:center; justify-content:center; color:var(--text-200);">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
        </div>
        <div style="display:flex; flex-direction:column; gap:2px;">
          <div style="font-size:12px; font-weight:700; color:#fff;">Operator</div>
          <div style="font-size:10px; color:var(--text-muted);">TC-Center</div>
        </div>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" stroke-width="2" style="margin-left:4px;"><polyline points="6 9 12 15 18 9"/></svg>
      </div>
    </div>
  `;
}

export function updateTopbar(title, subtitle) {
  const titleEl = document.getElementById('tb-title');
  const subEl = document.getElementById('tb-subtitle');
  if (titleEl && subEl) {
    titleEl.textContent = title;
    subEl.textContent = subtitle;
  }
}
