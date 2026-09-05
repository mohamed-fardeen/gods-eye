import { renderSidebar, updateSidebarActive } from './ui/Sidebar.js';
import { renderTopbar, updateTopbar } from './ui/Topbar.js';
import { renderDashboard, initDashboardMap } from './pages/Dashboard.js';
import { renderDigitalTwin, initMapOverlayEvents } from './pages/DigitalTwin.js';
import { renderCameras } from './pages/Cameras.js';
import { renderPlateSearch } from './pages/PlateSearch.js';
import { renderTraffic } from './pages/Traffic.js';
import { renderIncidents } from './pages/Incidents.js';
import { renderCameraManagement } from './pages/CameraManagement.js';
import { renderSettings } from './pages/Settings.js';



// Reports page
function renderReports() {
  return `<div class="page-padding page-fade">
    <div style="display:flex;justify-content:flex-end;gap:10px;margin-bottom:4px;">
      <select class="select-input"><option>Daily</option><option>Weekly</option><option>Monthly</option></select>
      <input type="date" class="search-input" value="2024-05-21"/>
      <button class="btn btn-primary">Generate Report</button>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
      ${[
        ['Traffic Summary Report','21 May 2024','PDF','345 KB','Ready'],
        ['Camera Activity Report','21 May 2024','Excel','1.2 MB','Ready'],
        ['ANPR Violations Report','21 May 2024','PDF','201 KB','Ready'],
        ['Incident Report','21 May 2024','PDF','122 KB','Ready'],
        ['Vehicle Count Report','20 May 2024','Excel','443 KB','Ready'],
        ['System Health Report','20 May 2024','PDF','88 KB','Ready'],
      ].map(([name, date, type, size, status]) => `
      <div class="panel">
        <div class="panel-body" style="display:flex;align-items:center;gap:14px;">
          <div class="kpi-icon-wrap blue" style="width:40px;height:40px;flex-shrink:0;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
          </div>
          <div style="flex:1;">
            <div style="font-size:13px;font-weight:600;">${name}</div>
            <div style="font-size:11px;color:var(--text-muted);margin-top:2px;">${date} · ${type} · ${size}</div>
          </div>
          <div style="display:flex;flex-direction:column;gap:6px;align-items:flex-end;">
            <span class="badge online">${status}</span>
            <button class="btn btn-ghost" style="padding:4px 10px;font-size:11px;">⬇ Download</button>
          </div>
        </div>
      </div>`).join('')}
    </div>
  </div>`;
}

const ROUTES = {
  '#/': {
    render: renderDashboard,
    title: 'COMMAND DASHBOARD',
    subtitle: 'Real-time overview of city traffic and incidents',
  },
  '#/map': {
    render: renderDigitalTwin,
    title: 'DIGITAL TWIN',
    subtitle: 'Interactive 3D geospatial city environment',
  },
  '#/cameras': {
    render: renderCameras,
    title: 'LIVE CAMERA FEEDS',
    subtitle: 'Real-time monitoring and AI detections',
  },
  '#/plate-search': {
    render: renderPlateSearch,
    title: 'PLATE SEARCH',
    subtitle: 'Search and track vehicles across the city',
  },
  '#/vehicle-profile': {
    render: () => {
      import('./pages/VehicleProfile.js').then(module => {
        document.getElementById('page-content').innerHTML = module.renderVehicleProfile();
        module.initVehicleProfileMap();
      });
      return '<div style="padding:24px; color:var(--text-muted);">Loading Vehicle Profile...</div>';
    },
    title: 'VEHICLE PROFILE',
    subtitle: 'Detailed information and movement history',
  },
  '#/traffic': {
    render: renderTraffic,
    title: 'TRAFFIC ANALYSIS',
    subtitle: 'Real-time traffic insights and historical trends',
  },
  '#/incidents': {
    render: renderIncidents,
    title: 'ALERTS & INCIDENTS',
    subtitle: 'Real-time alerts, incidents, and system notifications',
  },
  '#/reports': {
    render: renderReports,
    title: 'REPORTS',
    subtitle: 'Automated reporting and analytics exports',
  },
  '#/camera-management': {
    render: renderCameraManagement,
    title: 'CAMERA MANAGEMENT',
    subtitle: 'Monitor, configure and maintain the city camera network',
  },
  '#/settings': {
    render: renderSettings,
    title: 'SYSTEM SETTINGS',
    subtitle: 'Configuration and system status',
  },
};

class Router {
  constructor() {
    this.viewer = null;
    this.layerManager = null;
    window.addEventListener('hashchange', () => this.handleRouteChange());
  }

  init(viewer, layerManager) {
    this.viewer = viewer;
    this.layerManager = layerManager;

    renderSidebar();
    renderTopbar();

    if (!window.location.hash || window.location.hash === '#') {
      window.location.hash = '#/';
    } else {
      this.handleRouteChange();
    }
  }

  handleRouteChange() {
    const hash = window.location.hash || '#/';
    const route = ROUTES[hash] || ROUTES['#/'];

    updateSidebarActive(hash);
    updateTopbar(route.title, route.subtitle);

    const contentDiv = document.getElementById('page-content');
    const cesiumDiv = document.getElementById('cesiumContainer');

    if (hash === '#/map') {
      contentDiv.innerHTML = route.render();
      contentDiv.classList.add('map-mode');
      cesiumDiv.classList.add('active');
      initMapOverlayEvents(this.viewer, this.layerManager);
    } else {
      contentDiv.classList.remove('map-mode');
      cesiumDiv.classList.remove('active');
      contentDiv.innerHTML = route.render();
      if (hash === '#/') {
        initDashboardMap();
      } else if (hash === '#/plate-search') {
        import('./pages/PlateSearch.js').then(module => {
          if (module.initPlateSearchMap) module.initPlateSearchMap();
        });
      } else if (hash === '#/traffic') {
        import('./pages/Traffic.js').then(module => {
          if (module.initTrafficMap) module.initTrafficMap();
        });
      } else if (hash === '#/incidents') {
        import('./pages/Incidents.js').then(module => {
          if (module.initIncidentsMap) module.initIncidentsMap();
        });
      } else if (hash === '#/camera-management') {
        import('./pages/CameraManagement.js').then(module => {
          if (module.initCameraManagementMap) module.initCameraManagementMap();
        });
      }
    }
  }
}

export const router = new Router();
