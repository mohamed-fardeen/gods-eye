import * as Cesium from "cesium";

/**
 * Sets up Cesium World Terrain.
 * This is necessary so the ground imagery is elevated to real-world altitude,
 * preventing OSM 3D buildings and custom models from floating above the map.
 *
 * @param {Cesium.Viewer} viewer
 */
export async function setupTerrain(viewer) {
  try {
    const terrainProvider = await Cesium.createWorldTerrainAsync();
    viewer.terrainProvider = terrainProvider;
    console.log("[Terrain] Cesium World Terrain loaded for proper building clamping.");
  } catch (err) {
    console.warn("[Terrain] Falling back to standard flat ellipsoid terrain due to error:", err);
  }
}
