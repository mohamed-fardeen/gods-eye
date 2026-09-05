/**
 * Overpass API Service
 *
 * Fetches roads (motorway → tertiary) and all bridge ways for Chennai.
 * Bridge features receive embedded altitude coordinates for 3D rendering.
 */

const OVERPASS_ENDPOINT = "https://overpass-api.de/api/interpreter";

function buildQuery(bbox) {
  const { south, west, north, east } = bbox;
  return `[out:json][timeout:30];
(
  way["highway"~"^(motorway|trunk|primary|secondary|tertiary)$"]["bridge"!="yes"]
    (${south},${west},${north},${east});
  way["highway"]["bridge"="yes"]
    (${south},${west},${north},${east});
);
out geom;`;
}

function osmToGeoJson(osmData) {
  const roadFeatures = [];
  const bridgeFeatures = [];

  for (const element of osmData.elements) {
    if (element.type !== "way" || !element.geometry || element.geometry.length < 2) continue;

    const tags = element.tags ?? {};
    const isBridge = tags.bridge === "yes";
    const highway = tags.highway ?? "unclassified";
    const layer = isBridge ? Math.max(1, Number(tags.layer ?? 1)) : 0;
    const elevation = layer * 7.0; // ~7m per OSM layer above ground

    const coordinates = isBridge
      ? element.geometry.map((n) => [n.lon, n.lat, elevation])
      : element.geometry.map((n) => [n.lon, n.lat]);

    const feature = {
      type: "Feature",
      geometry: { type: "LineString", coordinates },
      properties: {
        id: element.id,
        highway,
        name: tags.name ?? "",
        bridge: isBridge,
        layer,
        oneway: tags.oneway ?? "no",
        maxspeed: tags.maxspeed ?? null,
      },
    };

    (isBridge ? bridgeFeatures : roadFeatures).push(feature);
  }

  return {
    roads: { type: "FeatureCollection", features: roadFeatures },
    bridges: { type: "FeatureCollection", features: bridgeFeatures },
  };
}

/**
 * @returns {Promise<{ roads: GeoJSON.FeatureCollection, bridges: GeoJSON.FeatureCollection }>}
 */
export async function fetchChennaiRoads(bbox = {
  south: 12.960,
  west: 80.160,
  north: 13.140,
  east: 80.330,
}) {
  const query = buildQuery(bbox);
  console.log("[Overpass] Fetching Chennai roads & bridges…");

  const response = await fetch(OVERPASS_ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: `data=${encodeURIComponent(query)}`,
  });

  if (!response.ok) throw new Error(`Overpass HTTP ${response.status}`);

  const osmData = await response.json();
  if (!Array.isArray(osmData.elements)) throw new Error("Unexpected Overpass response");

  const { roads, bridges } = osmToGeoJson(osmData);
  console.log(`[Overpass] ${roads.features.length} roads + ${bridges.features.length} bridges.`);
  return { roads, bridges };
}
