import * as Cesium from "cesium";
import { BaseLayer } from "./BaseLayer.js";

/**
 * BuildingsLayer — Cesium OSM 3D Buildings with height-based styling.
 *
 * Styling uses OSM `height` tag (a number in Cesium's processed tiles):
 *   > 45m → steel-blue glass  (skyscrapers / towers)
 *   > 25m → pale blue-white   (mid-rise commercial)
 *   >  8m → warm off-white    (standard multi-storey)
 *   default → warm Chennai masonry palette
 */
export class BuildingsLayer extends BaseLayer {
  constructor() {
    super("osm-buildings", "Cesium OSM Buildings");
    /** @type {Cesium.Cesium3DTileset | null} */
    this.tileset = null;
  }

  async init(viewer) {
    await super.init(viewer);

    try {
      console.log("[BuildingsLayer] Loading Cesium OSM Buildings…");
      this.tileset = await Cesium.createOsmBuildingsAsync();

      // Tune tileset LOD for performance — 32 significantly reduces geometry count
      this.tileset.maximumScreenSpaceError = 32;

      // Height-based colour style.
      // Use a "defines" block to create a guaranteed numeric variable.
      // This prevents the "undefined and 45" runtime crash since Cesium's
      // expression engine evaluates both sides of the condition simultaneously.
      this.tileset.style = new Cesium.Cesium3DTileStyle({
        defines: {
          // If cesium_estimatedHeight is undefined, fallback to 0
          safeHeight: "${cesium_estimatedHeight} === undefined ? 0 : ${cesium_estimatedHeight}"
        },
        color: {
          conditions: [
            // Skyscrapers / towers — steel-blue glass
            ["${safeHeight} >= 45", "color('#78B4E8', 0.78)"],
            // Mid-rise commercial — pale blue glass
            ["${safeHeight} >= 25", "color('#A8CDEA', 0.84)"],
            // Multi-storey — off-white modern
            ["${safeHeight} >= 8",  "color('#E8E3DD', 0.90)"],
            // All others / untagged — warm Chennai masonry
            ["true", "color('#CEC4BB', 0.92)"],
          ],
        },
      });

      viewer.scene.primitives.add(this.tileset);
      this._isLoaded = true;
      console.log("[BuildingsLayer] Loaded with height-aware glass styling.");
    } catch (err) {
      console.error(
        "[BuildingsLayer] Failed to load OSM Buildings. Check VITE_CESIUM_ION_TOKEN in .env.local.",
        err
      );
      this._isLoaded = false;
    }
  }

  show() {
    super.show();
    if (this.tileset) this.tileset.show = true;
  }

  hide() {
    super.hide();
    if (this.tileset) this.tileset.show = false;
  }

  destroy() {
    if (this.tileset && this.viewer) {
      this.viewer.scene.primitives.remove(this.tileset);
      this.tileset = null;
    }
    super.destroy();
  }
}
