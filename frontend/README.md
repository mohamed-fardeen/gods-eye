# Chennai Digital Twin / God's Eye (Phase 1)

An interactive, browser-based 3D digital twin foundation for **Chennai, Tamil Nadu, India**, built using **CesiumJS**, **Vite**, and real **Cesium OSM Buildings** geospatial data.

This forms the static 3D foundation for city-scale traffic intelligence, designed to accept future infrastructure and sensor layers (CCTV, ANPR, traffic signals, vehicle trajectories, etc.) without re-architecting the core viewer.

---

## Features (Phase 1)

* **Real 3D City Streaming**: Streams real OpenStreetMap-derived 3D buildings for Chennai using Cesium Ion 3D Tiles (`createOsmBuildingsAsync`).
* **Accurate Geographic Positioning**: Anchored at verified coordinates for Chennai (`13.0827° N, 80.2707° E`) with a tailored initial camera perspective (~1,200m altitude, oblique pitch) so urban structures are immediately visible.
* **OpenStreetMap Base Imagery**: High-resolution OpenStreetMap raster tile base layer rendering streets, waterways, and coastline.
* **Optional World Terrain**: Configured to load Cesium World Terrain asynchronously with automatic graceful fallback to the ellipsoid globe if restricted or unavailable.
* **Modular Layer Architecture**: Decoupled Cesium viewer, geographic configuration, and layer management (`BaseLayer`, `LayerManager`, `BuildingsLayer`).
* **Minimal HUD**: Fast navigation to key landmarks (*Chennai Home*, *Chennai Central*, *Marina Beach*) and 3D buildings visibility toggle.

---

## Directory Structure

```
3d-twin/
├── index.html              # HTML entry point with fullscreen container & HUD overlay
├── package.json            # Project dependencies & scripts
├── vite.config.js          # Vite config with static copy for Cesium assets
├── .env.example            # Environment template for Cesium Ion token
├── .gitignore              # Ignores node_modules, dist, and .env.local
├── README.md               # Documentation and setup guide
└── src/
    ├── main.js             # Bootstrap & lifecycle orchestrator
    ├── style.css           # Fullscreen layout & glassmorphic HUD styling
    ├── config/
    │   └── coordinates.js  # Verified coordinates, initial camera pose, & bounds
    ├── cesium/
    │   ├── viewer.js       # Cesium Viewer initialization & OSM base layer
    │   ├── terrain.js      # Optional World Terrain with graceful fallback
    │   └── camera.js       # Camera navigation & landmark flyTo controllers
    ├── layers/
    │   ├── BaseLayer.js    # Abstract layer interface
    │   ├── LayerManager.js # Registry & coordinator for digital twin layers
    │   └── BuildingsLayer.js # Real Cesium OSM 3D Buildings streaming
    └── ui/
        └── hud.js          # Minimal HUD controls (bookmarks & layer toggles)
```

---

## Prerequisites

* **Node.js**: v18.0.0 or higher (v20+ recommended)
* **npm**: v9.0.0 or higher
* **Cesium Ion Access Token** (Free): Required to stream Cesium OSM Buildings and Cesium World Terrain.

---

## Setup Instructions

### 1. Clone & Install Dependencies

```bash
cd "3d twin"
npm install
```

### 2. Configure Cesium Ion Token

Cesium OSM Buildings are hosted on Cesium Ion and require an access token.

1. Sign up for a free account at [cesium.com/ion](https://ion.cesium.com/).
2. Go to **Access Tokens** in your Cesium Ion dashboard and copy your default token (or create a new one with "Cesium OSM Buildings" permission).
3. Create a `.env.local` file in the project root:

```bash
cp .env.example .env.local
```

4. Add your token to `.env.local`:

```env
VITE_CESIUM_ION_TOKEN=your_cesium_ion_token_here
```

> **Security Note:** `.env.local` is already listed in `.gitignore` so your private token will never be committed to source control.

---

## Running Locally

Start the Vite development server:

```bash
npm run dev
```

Open your browser and navigate to:

```
http://localhost:3000
```

### Controls

* **Left Click + Drag**: Pan / rotate around globe
* **Right Click + Drag / Scroll**: Zoom in and out
* **Middle Click + Drag / Ctrl + Left Drag**: Tilt and change camera pitch
* **HUD Buttons**:
  * **Chennai Home**: Returns to the urban core overview.
  * **Chennai Central**: Flies to Chennai Central Railway Station & Ripon Building.
  * **Marina Beach**: Oblique view across the Marina Beach coastline.
  * **Toggle Switch**: Toggles 3D OSM Buildings on/off.

---

## Building for Production

To create an optimized production build:

```bash
npm run build
```

To preview the production build locally:

```bash
npm run preview
```

---

## Architecture & Extensibility

### Layer Lifecycle
Every digital twin data layer extends `BaseLayer`:
* `init(viewer)`: Asynchronous setup and asset retrieval.
* `show()` / `hide()`: Toggles primitive/entity visibility.
* `destroy()`: Cleans up primitives from the Cesium scene.

`LayerManager` coordinates registration, lookup, and visibility across all layers.

### Phase 2 Roadmap
In Phase 2, real Chennai road networks and infrastructure coordinates will be introduced:
* Roads network (OSM GeoJSON/vector tiles)
* CCTV camera coordinates & FOV frustums
* Traffic signal locations & status indicators
* Operational monitoring zones
