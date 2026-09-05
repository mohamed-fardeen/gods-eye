import * as Cesium from "cesium";
import "cesium/Build/Cesium/Widgets/widgets.css";
import { CHENNAI_GEOGRAPHY } from "../config/coordinates.js";
import { flyToInitialPosition } from "./camera.js";

/**
 * Initializes the Cesium Viewer stripped down exclusively for Chennai.
 * - Restricts the globe strictly to Chennai bounds (cartographicLimitRectangle).
 * - Bypasses default outer-space camera view (no globe zoom animation).
 * - Strips unnecessary globe shaders (atmosphere, fog, world-wide tiles).
 *
 * @param {string} containerId DOM ID for viewer element (default 'cesiumContainer')
 * @returns {Promise<Cesium.Viewer>}
 */
export async function initViewer(containerId = "cesiumContainer") {
  // Read Ion access token from Vite environment variables (.env.local)
  const ionToken = import.meta.env.VITE_CESIUM_ION_TOKEN;

  if (ionToken) {
    Cesium.Ion.defaultAccessToken = ionToken;
    console.log("[Cesium] Cesium Ion access token configured from environment.");
  } else {
    console.warn(
      "[Cesium] VITE_CESIUM_ION_TOKEN is not defined in .env.local."
    );
  }

  // Define Chennai bounding box
  const chennaiBounds = Cesium.Rectangle.fromDegrees(
    CHENNAI_GEOGRAPHY.bounds.west,
    CHENNAI_GEOGRAPHY.bounds.south,
    CHENNAI_GEOGRAPHY.bounds.east,
    CHENNAI_GEOGRAPHY.bounds.north
  );

  // Set Cesium default view so internal setup never defaults to outer space / whole earth
  Cesium.Camera.DEFAULT_VIEW_RECTANGLE = chennaiBounds;
  Cesium.Camera.DEFAULT_VIEW_FACTOR = 0;

  // Base imagery layer (clipped to Chennai rectangle)
  let baseLayer;
  if (ionToken) {
    try {
      const ionProvider = await Cesium.createWorldImageryAsync({
        style: Cesium.IonWorldImageryStyle.AERIAL_WITH_LABELS,
      });
      baseLayer = new Cesium.ImageryLayer(ionProvider, {
        rectangle: chennaiBounds,
      });
      console.log("[Cesium] Loaded Cesium Ion world aerial imagery (clipped to Chennai).");
    } catch (err) {
      console.warn("[Cesium] Could not load Ion world imagery, falling back to OSM tiles:", err);
    }
  }

  if (!baseLayer) {
    baseLayer = new Cesium.ImageryLayer(
      new Cesium.OpenStreetMapImageryProvider({
        url: "https://tile.openstreetmap.org/",
        rectangle: chennaiBounds,
      })
    );
  }

  const viewer = new Cesium.Viewer(containerId, {
    baseLayer,
    baseLayerPicker: false,

    // Controls: disable unnecessary widgets for maximum startup speed
    animation: false,
    timeline: false,
    geocoder: false,
    homeButton: false,
    sceneModePicker: false,
    navigationHelpButton: false,
    selectionIndicator: false,
    infoBox: false,
    fullscreenButton: false,

    // Rendering & performance optimizations
    requestRenderMode: true,           // ONLY render when camera moves or data changes
    maximumRenderTimeChange: Infinity,
    scene3DOnly: true,                 // Disables 2D/Columbus view, saves memory
    maximumScreenSpaceError: 16,       // Base terrain/imagery LOD
  });

  // Strip the globe down strictly to Chennai:
  // Culls every tile outside Chennai, avoiding world-wide quadtree downloads
  viewer.scene.globe.cartographicLimitRectangle = chennaiBounds;

  // Immediately set camera view to Chennai before the first frame is painted
  flyToInitialPosition(viewer, false);

  // Restrict camera zoom so user stays within Chennai digital twin scope
  const controller = viewer.scene.screenSpaceCameraController;
  controller.maximumZoomDistance = 45000; // max 45km altitude
  controller.minimumZoomDistance = 30;    // min 30m altitude

  // Performance: Lower resolution slightly for integrated/low-end GPUs
  viewer.resolutionScale = 0.85;
  viewer.scene.postProcessStages.fxaa.enabled = false;

  // Strip globe atmosphere and fog to eliminate heavy shader passes
  if (viewer.scene.skyAtmosphere) {
    viewer.scene.skyAtmosphere.show = false;
  }
  viewer.scene.globe.showGroundAtmosphere = false;
  viewer.scene.globe.enableLighting = false;
  viewer.scene.globe.depthTestAgainstTerrain = false;
  viewer.scene.fog.enabled = false;

  return viewer;
}
