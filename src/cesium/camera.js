import * as Cesium from "cesium";
import { CHENNAI_GEOGRAPHY } from "../config/coordinates.js";

/**
 * Flies the camera to the initial Chennai urban view.
 * Configured at an oblique 3D angle so buildings are immediately visible.
 *
 * @param {Cesium.Viewer} viewer
 * @param {boolean} [animate=true] Whether to smoothly animate the camera
 */
export function flyToInitialPosition(viewer, animate = true) {
  const { destination, orientation, duration } = CHENNAI_GEOGRAPHY.initialCamera;

  const targetCartesian = Cesium.Cartesian3.fromDegrees(
    destination.longitude,
    destination.latitude,
    destination.height
  );

  const targetOrientation = {
    heading: Cesium.Math.toRadians(orientation.headingDegrees),
    pitch: Cesium.Math.toRadians(orientation.pitchDegrees),
    roll: Cesium.Math.toRadians(orientation.rollDegrees),
  };

  if (animate) {
    viewer.camera.flyTo({
      destination: targetCartesian,
      orientation: targetOrientation,
      duration: duration || 3.0,
      easingFunction: Cesium.EasingFunction.QUADRATIC_OUT,
    });
  } else {
    viewer.camera.setView({
      destination: targetCartesian,
      orientation: targetOrientation,
    });
  }
}

/**
 * Flies the camera to a predefined Chennai landmark.
 *
 * @param {Cesium.Viewer} viewer
 * @param {'home' | 'central' | 'marina'} landmarkKey
 */
export function flyToLandmark(viewer, landmarkKey) {
  const landmark = CHENNAI_GEOGRAPHY.landmarks[landmarkKey];
  if (!landmark) {
    console.warn(`[Camera] Landmark "${landmarkKey}" not found in coordinates configuration.`);
    return;
  }

  viewer.camera.flyTo({
    destination: Cesium.Cartesian3.fromDegrees(
      landmark.longitude,
      landmark.latitude,
      landmark.height
    ),
    orientation: {
      heading: Cesium.Math.toRadians(landmark.headingDegrees),
      pitch: Cesium.Math.toRadians(landmark.pitchDegrees),
      roll: Cesium.Math.toRadians(landmark.rollDegrees),
    },
    duration: 2.0,
    easingFunction: Cesium.EasingFunction.CUBIC_IN_OUT,
  });
}
