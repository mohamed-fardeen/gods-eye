/**
 * Abstract Base Layer class for Chennai Digital Twin.
 * All layers (buildings in Phase 1, roads/cameras/vehicles in future phases) implement this interface.
 */
export class BaseLayer {
  /**
   * @param {string} id Unique identifier for the layer
   * @param {string} name Human-readable display name
   */
  constructor(id, name) {
    if (new.target === BaseLayer) {
      throw new TypeError("Cannot construct BaseLayer instances directly.");
    }
    this.id = id;
    this.name = name;
    this.viewer = null;
    this._visible = true;
    this._isLoaded = false;
  }

  /**
   * Initialize the layer with the Cesium Viewer instance.
   * @param {import('cesium').Viewer} viewer
   * @returns {Promise<void>}
   */
  async init(viewer) {
    this.viewer = viewer;
  }

  /**
   * Show layer.
   */
  show() {
    this._visible = true;
  }

  /**
   * Hide layer.
   */
  hide() {
    this._visible = false;
  }

  /**
   * Toggle layer visibility.
   * @returns {boolean} New visibility state
   */
  toggle() {
    if (this._visible) {
      this.hide();
    } else {
      this.show();
    }
    return this._visible;
  }

  /**
   * Check if layer is currently visible.
   * @returns {boolean}
   */
  isVisible() {
    return this._visible;
  }

  /**
   * Check if layer has finished loading its resources.
   * @returns {boolean}
   */
  isLoaded() {
    return this._isLoaded;
  }

  /**
   * Clean up layer resources.
   */
  destroy() {
    this.hide();
    this.viewer = null;
    this._isLoaded = false;
  }
}
