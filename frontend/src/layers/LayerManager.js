/**
 * LayerManager - Central registry and lifecycle coordinator for all digital twin layers.
 */
export class LayerManager {
  /**
   * @param {import('cesium').Viewer} viewer
   */
  constructor(viewer) {
    this.viewer = viewer;
    /** @type {Map<string, import('./BaseLayer.js').BaseLayer>} */
    this.layers = new Map();
  }

  /**
   * Register and initialize a new layer.
   * @param {import('./BaseLayer.js').BaseLayer} layer
   * @returns {Promise<void>}
   */
  async register(layer) {
    if (this.layers.has(layer.id)) {
      console.warn(`[LayerManager] Layer with id "${layer.id}" is already registered. Skipping.`);
      return;
    }

    this.layers.set(layer.id, layer);
    try {
      await layer.init(this.viewer);
      console.log(`[LayerManager] Layer "${layer.name}" (${layer.id}) initialized successfully.`);
    } catch (error) {
      console.error(`[LayerManager] Error initializing layer "${layer.name}":`, error);
    }
  }

  /**
   * Retrieve a registered layer by id.
   * @param {string} id
   * @returns {import('./BaseLayer.js').BaseLayer | undefined}
   */
  get(id) {
    return this.layers.get(id);
  }

  /**
   * Show a layer.
   * @param {string} id
   */
  show(id) {
    const layer = this.layers.get(id);
    if (layer) {
      layer.show();
    }
  }

  /**
   * Hide a layer.
   * @param {string} id
   */
  hide(id) {
    const layer = this.layers.get(id);
    if (layer) {
      layer.hide();
    }
  }

  /**
   * Toggle visibility of a layer.
   * @param {string} id
   * @returns {boolean | undefined}
   */
  toggle(id) {
    const layer = this.layers.get(id);
    if (layer) {
      return layer.toggle();
    }
    return undefined;
  }

  /**
   * Get all registered layers.
   * @returns {import('./BaseLayer.js').BaseLayer[]}
   */
  getAll() {
    return Array.from(this.layers.values());
  }

  /**
   * Destroy all layers and clean up.
   */
  destroy() {
    for (const layer of this.layers.values()) {
      layer.destroy();
    }
    this.layers.clear();
    this.viewer = null;
  }
}
