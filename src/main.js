import { initViewer } from "./cesium/viewer.js";
import { setupTerrain } from "./cesium/terrain.js";
import { flyToInitialPosition } from "./cesium/camera.js";
import { LayerManager } from "./layers/LayerManager.js";
import { BuildingsLayer } from "./layers/BuildingsLayer.js";
import { RoadsLayer } from "./layers/RoadsLayer.js";
import { router } from "./router.js";

/**
 * Main application bootstrap for Chennai Digital Twin (SPA).
 */
async function bootstrap() {
  console.log("[App] Initializing Chennai Digital Twin (God's Eye) SPA…");

  try {
    // 1. Core Cesium viewer
    const viewer = await initViewer("cesiumContainer");

    // Use setView (instant) — no globe spin animation on startup
    flyToInitialPosition(viewer, false);

    // 2. Layer registry
    const layerManager = new LayerManager(viewer);

    // 3. Initialize Router (builds app shell & renders initial page)
    router.init(viewer, layerManager);

    // 4. 3D Buildings (Cesium OSM, streams on demand)
    const buildingsLayer = new BuildingsLayer();
    await layerManager.register(buildingsLayer);

    // 5. Road network + bridges — async, non-blocking
    const roadsLayer = new RoadsLayer();
    layerManager.register(roadsLayer).then(() => {
      console.log("[App] Roads layer loaded");
    });

    // 6. Optional terrain — graceful fallback
    setupTerrain(viewer).catch((err) => {
      console.warn("[App] Optional terrain failed gracefully:", err);
    });

    console.log("[App] Chennai Digital Twin initialization complete.");
  } catch (error) {
    console.error("[App] Fatal initialization error:", error);
  }
}

window.addEventListener("DOMContentLoaded", bootstrap);
