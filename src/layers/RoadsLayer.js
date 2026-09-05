import * as Cesium from "cesium";
import { BaseLayer } from "./BaseLayer.js";
import { fetchChennaiRoads } from "../services/overpass.js";

/**
 * Visual style per OSM highway type.
 * Width is used in GroundPolylineGeometry (per-geometry, not per-appearance).
 */
const ROAD_STYLES = {
  motorway: { color: Cesium.Color.fromCssColorString("#f59e0b"), width: 6.0 },
  trunk:    { color: Cesium.Color.fromCssColorString("#fb923c"), width: 5.0 },
  primary:  { color: Cesium.Color.fromCssColorString("#38bdf8"), width: 4.0 },
  secondary:{ color: Cesium.Color.fromCssColorString("#94a3b8"), width: 2.8 },
  tertiary: { color: Cesium.Color.fromCssColorString("#4b5563"), width: 1.8 },
  default:  { color: Cesium.Color.fromCssColorString("#374151"), width: 1.4 },
};

function getRoadStyle(highway) {
  return ROAD_STYLES[highway] ?? ROAD_STYLES.default;
}

/**
 * RoadsLayer
 *
 * Roads  → GroundPolylinePrimitive (one primitive per road type = ~5 draw calls total, very fast)
 * Bridges → CorridorGraphics (3D deck slab) + CylinderGraphics (support pillars)
 */
export class RoadsLayer extends BaseLayer {
  constructor() {
    super("roads", "Road Network");
    /** @type {Cesium.GroundPolylinePrimitive[]} */
    this._primitives = [];
    /** @type {Cesium.Entity[]} */
    this._bridgeEntities = [];
    /** @type {'idle'|'loading'|'loaded'|'error'} */
    this.status = "idle";
    this.errorMessage = null;
  }

  async init(viewer) {
    await super.init(viewer);
    this.status = "loading";

    try {
      const { roads, bridges } = await fetchChennaiRoads();
      this._buildGroundRoads(viewer, roads.features);
      this._buildBridgeStructures(viewer, bridges.features);

      this._isLoaded = true;
      this.status = "loaded";
      console.log(
        `[RoadsLayer] ${roads.features.length} road segs in ${this._primitives.length} draw calls. ` +
        `${bridges.features.length} bridges as 3D structures.`
      );
    } catch (err) {
      this.status = "error";
      this.errorMessage = err.message;
      console.error("[RoadsLayer] Failed:", err);
    }
  }

  /**
   * Batches roads into ONE GroundPolylinePrimitive per highway type.
   * Entire road network = ~5 GPU draw calls instead of thousands.
   */
  _buildGroundRoads(viewer, features) {
    // Group features by highway type
    const groups = new Map();
    for (const f of features) {
      const hw = f.properties.highway ?? "default";
      if (!groups.has(hw)) groups.set(hw, []);
      groups.get(hw).push(f);
    }

    for (const [highway, feats] of groups) {
      const { color, width } = getRoadStyle(highway);

      const instances = [];
      for (const f of feats) {
        const coords = f.geometry.coordinates;
        if (!coords || coords.length < 2) continue;
        // coords are [lon, lat] pairs — flatten to [lon, lat, lon, lat, ...]
        const flat = [];
        for (const c of coords) { flat.push(c[0], c[1]); }
        const positions = Cesium.Cartesian3.fromDegreesArray(flat);
        if (positions.length < 2) continue;

        instances.push(new Cesium.GeometryInstance({
          geometry: new Cesium.GroundPolylineGeometry({ positions, width }),
        }));
      }

      if (instances.length === 0) continue;

      const prim = new Cesium.GroundPolylinePrimitive({
        geometryInstances: instances,
        appearance: new Cesium.PolylineMaterialAppearance({
          material: Cesium.Material.fromType("Color", { color: color.withAlpha(0.92) }),
        }),
        asynchronous: true,
      });

      viewer.scene.primitives.add(prim);
      this._primitives.push(prim);
    }
  }

  /**
   * Renders each bridge as a real 3D structure:
   *  - Deck slab (CorridorGraphics with extrudedHeight)
   *  - Road surface colour layer on top of the deck
   *  - Tapered support pillars (CylinderGraphics) at each node + midpoints
   */
  _buildBridgeStructures(viewer, features) {
    for (const f of features) {
      const coords = f.geometry.coordinates;
      if (!coords || coords.length < 2) continue;

      const highway    = f.properties.highway ?? "primary";
      const elevation  = coords[0][2] ?? 8.0;    // z from GeoJSON (set by overpass.js)
      const deckBottom = elevation - 1.5;
      const deckTop    = elevation;
      const deckWidth  = ["motorway", "trunk"].includes(highway) ? 22 : 15;
      const { color }  = getRoadStyle(highway);

      // Flat positions (no z) for CorridorGraphics
      const flat = [];
      for (const c of coords) { flat.push(c[0], c[1]); }
      const positions = Cesium.Cartesian3.fromDegreesArray(flat);

      // ── Deck slab (concrete underside) ──────────────────────────────────
      this._bridgeEntities.push(viewer.entities.add({
        corridor: {
          positions,
          width: deckWidth,
          height: deckBottom,
          extrudedHeight: deckTop,
          material: Cesium.Color.fromCssColorString("#7f8fa6"),
          outline: true,
          outlineColor: Cesium.Color.fromCssColorString("#2d3748"),
          outlineWidth: 1,
          shadows: Cesium.ShadowMode.ENABLED,
        },
      }));

      // ── Road surface (thin coloured layer on top of the slab) ────────────
      this._bridgeEntities.push(viewer.entities.add({
        corridor: {
          positions,
          width: deckWidth - 2.5,
          height: deckTop,
          extrudedHeight: deckTop + 0.25,
          material: color.withAlpha(0.95),
          outline: false,
        },
      }));

      // ── Edge kerbs (two narrow slabs along the sides) ────────────────────
      const kerbColor = Cesium.Color.fromCssColorString("#c0c8d4");
      // We simulate kerbs by a slightly wider, slightly raised outline corridor
      this._bridgeEntities.push(viewer.entities.add({
        corridor: {
          positions,
          width: deckWidth + 0.8,
          height: deckTop - 0.1,
          extrudedHeight: deckTop + 0.4,
          material: kerbColor,
          outline: false,
          // Hollow look: Cesium doesn't natively support hollow corridors, so
          // the road surface layer on top masks the interior.
        },
      }));

      // ── Support pillars at each node + midpoints ─────────────────────────
      const pillarH = deckBottom; // height from sea-level ground to deck underside
      if (pillarH > 2) {
        const pillarPoints = [];
        for (let i = 0; i < coords.length; i++) {
          pillarPoints.push([coords[i][0], coords[i][1]]);
          if (i < coords.length - 1) {
            pillarPoints.push([
              (coords[i][0] + coords[i + 1][0]) / 2,
              (coords[i][1] + coords[i + 1][1]) / 2,
            ]);
          }
        }

        for (const [lon, lat] of pillarPoints) {
          this._bridgeEntities.push(viewer.entities.add({
            position: Cesium.Cartesian3.fromDegrees(lon, lat, pillarH / 2),
            cylinder: {
              length: pillarH,
              topRadius: 1.3,
              bottomRadius: 2.2,
              material: Cesium.Color.fromCssColorString("#606e7d"),
              outline: false,
              shadows: Cesium.ShadowMode.ENABLED,
            },
          }));
        }
      }
    }
  }

  show() {
    super.show();
    for (const p of this._primitives)     p.show = true;
    for (const e of this._bridgeEntities) e.show = true;
  }

  hide() {
    super.hide();
    for (const p of this._primitives)     p.show = false;
    for (const e of this._bridgeEntities) e.show = false;
  }

  destroy() {
    if (this.viewer) {
      for (const p of this._primitives)     this.viewer.scene.primitives.remove(p);
      for (const e of this._bridgeEntities) this.viewer.entities.remove(e);
    }
    this._primitives = [];
    this._bridgeEntities = [];
    super.destroy();
  }
}
