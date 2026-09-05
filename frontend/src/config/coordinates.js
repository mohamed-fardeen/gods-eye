/**
 * Chennai Digital Twin - Geographic Configuration
 *
 * Real, verified coordinates for Chennai, Tamil Nadu, India.
 * All angles in radians (Cesium.Math.toRadians) or degrees as indicated.
 */

export const CHENNAI_GEOGRAPHY = {
  // Chennai City Center (Central Business District / Ripon Building / Central Station)
  center: {
    longitude: 80.2707,
    latitude: 13.0827,
    height: 0,
  },

  // Initial Camera Pose: Close oblique over central Chennai CBD.
  // Uses setView() (instant) — no globe-spin animation on startup.
  initialCamera: {
    destination: {
      longitude: 80.2820,
      latitude: 13.0700,
      height: 900.0,   // ~900m — buildings clearly visible, city fills viewport
    },
    orientation: {
      headingDegrees: 10.0,
      pitchDegrees: -38.0,  // steeper downward look for immediate depth
      rollDegrees: 0.0,
    },
    duration: 3.0,
  },

  // Greater Chennai Metropolitan Area Bounding Coordinates
  bounds: {
    west: 80.000,
    south: 12.834,
    east: 80.340,
    north: 13.250,
  },

  // Initial Operational / Test Zone (Central Urban Corridor)
  operationalZone: {
    name: "Central Chennai Urban Core",
    description: "High-density urban corridor spanning Chennai Central, Anna Salai, and Marina Coast",
    west: 80.220,
    south: 13.030,
    east: 80.300,
    north: 13.100,
  },

  // Key Phase 1 Landmarks for navigation
  landmarks: {
    home: {
      name: "Chennai Overview",
      longitude: 80.2820,
      latitude: 13.0700,
      height: 1800.0,
      headingDegrees: 10.0,
      pitchDegrees: -35.0,
      rollDegrees: 0.0,
    },
    central: {
      name: "Chennai Central",
      // Chennai Central Railway Station at Periyamet
      longitude: 80.2765,
      latitude: 13.0828,
      height: 600.0,
      headingDegrees: 5.0,   // Looking roughly north toward George Town
      pitchDegrees: -25.0,
      rollDegrees: 0.0,
    },
    marina: {
      name: "Marina Beach",
      // Marina Beach promenade, central stretch
      longitude: 80.2920,
      latitude: 13.0590,
      height: 900.0,
      headingDegrees: 270.0, // Looking west inland from the Bay of Bengal coastline
      pitchDegrees: -22.0,
      rollDegrees: 0.0,
    },
  },
};
