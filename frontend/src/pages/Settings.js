export function renderSettings() {
  return `<div class="page-padding page-fade" style="max-width:900px;margin:0 auto;width:100%;">

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">

      <!-- Platform Info -->
      <div class="panel">
        <div class="panel-hdr"><span class="panel-title">Platform Configuration</span></div>
        <div class="panel-body">
          <div class="data-row"><span class="data-key">Platform Name</span><span class="data-val">God's Eye Command Center</span></div>
          <div class="data-row"><span class="data-key">City</span><span class="data-val">Chennai, Tamil Nadu</span></div>
          <div class="data-row"><span class="data-key">Environment</span><span class="data-val">Development</span></div>
          <div class="data-row"><span class="data-key">Version</span><span class="data-val">1.0.0</span></div>
          <div class="data-row"><span class="data-key">Build</span><span class="data-val">2024.05.21</span></div>
          <div class="data-row" style="border:none;"><span class="data-key">Timezone</span><span class="data-val">IST (UTC +5:30)</span></div>
        </div>
      </div>

      <!-- Cesium Map Engine -->
      <div class="panel">
        <div class="panel-hdr"><span class="panel-title">Map Engine (Cesium)</span></div>
        <div class="panel-body">
          <div class="data-row"><span class="data-key">3D Engine</span><span class="data-val" style="color:var(--cyan);">CesiumJS</span></div>
          <div class="data-row"><span class="data-key">Cesium Ion Token</span><span class="data-val" style="color:var(--text-muted);">Loaded via .env.local</span></div>
          <div class="data-row"><span class="data-key">Terrain Provider</span><span class="data-val">Cesium World Terrain</span></div>
          <div class="data-row"><span class="data-key">Base Imagery</span><span class="data-val">Aerial with Labels</span></div>
          <div class="data-row"><span class="data-key">Buildings</span><span class="data-val">Cesium OSM Buildings</span></div>
          <div class="data-row" style="border:none;"><span class="data-key">Road Provider</span><span class="data-val">Overpass API</span></div>
        </div>
      </div>

      <!-- System Services -->
      <div class="panel">
        <div class="panel-hdr"><span class="panel-title">System Services</span></div>
        <div class="panel-body" style="padding:8px 14px;">
          ${[
            ['CesiumJS 3D Map Engine','Operational','green'],
            ['Vite Dev Server','Running','green'],
            ['OSM Building Tiles','Connected','green'],
            ['Overpass Road API','Connected','green'],
            ['AI Detection Engine','Pending','amber'],
            ['ANPR System','Pending','amber'],
            ['Real-time Video Streams','Pending','amber'],
            ['Incident Alert System','Pending','amber'],
          ].map(([name, status, color]) => `
          <div class="sys-row">
            <div class="sys-dot ${color==='green'?'on':'off'}" style="${color==='amber'?'background:var(--amber);box-shadow:0 0 6px var(--amber);':''}"></div>
            <div class="sys-info">
              <div class="sys-name">${name}</div>
              <div class="sys-status-text ${color==='green'?'on':''}" style="${color==='amber'?'color:var(--amber);':''};">${status}</div>
            </div>
          </div>`).join('')}
        </div>
      </div>

      <!-- Developer Notes -->
      <div class="panel">
        <div class="panel-hdr"><span class="panel-title">Developer Notes</span></div>
        <div class="panel-body">
          <div style="font-size:12px;color:var(--text-dim);line-height:1.8;">
            <div style="display:flex;gap:8px;align-items:flex-start;padding:6px 0;border-bottom:1px solid var(--border);">
              <span style="color:var(--green);margin-top:2px;">●</span>
              <span><strong style="color:var(--text-100);">Spatial Foundation:</strong> Interactive 3D map with OSM buildings, road network, and bridge geometry is fully operational.</span>
            </div>
            <div style="display:flex;gap:8px;align-items:flex-start;padding:6px 0;border-bottom:1px solid var(--border);">
              <span style="color:var(--green);margin-top:2px;">●</span>
              <span><strong style="color:var(--text-100);">SPA Architecture:</strong> Hash-based router — Cesium map initializes once and is toggled via CSS to preserve GPU state across navigation.</span>
            </div>
            <div style="display:flex;gap:8px;align-items:flex-start;padding:6px 0;border-bottom:1px solid var(--border);">
              <span style="color:var(--amber);margin-top:2px;">●</span>
              <span><strong style="color:var(--text-100);">AI / Video Modules:</strong> All camera, ANPR, traffic flow, and incident detection systems are UI demonstrations — real integrations are planned for future development.</span>
            </div>
            <div style="display:flex;gap:8px;align-items:flex-start;padding:6px 0;">
              <span style="color:var(--blue);margin-top:2px;">●</span>
              <span><strong style="color:var(--text-100);">Ion Token:</strong> Set <code style="background:var(--bg-700);padding:1px 6px;border-radius:3px;font-size:11px;">VITE_CESIUM_ION_TOKEN</code> in <code style="background:var(--bg-700);padding:1px 6px;border-radius:3px;font-size:11px;">.env.local</code> for aerial imagery.</span>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>`;
}
