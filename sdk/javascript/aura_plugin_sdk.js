/**
 * AURA Plugin SDK for JavaScript / Node.js Developers.
 * Provides base interface and helper functions for developing AURA plugins.
 */

class AuraPlugin {
  constructor(pluginId) {
    self.pluginId = pluginId;
  }

  initialize() {
    throw new Error("Plugin initialize() must be implemented.");
  }

  getTools() {
    return [];
  }
}

module.exports = { AuraPlugin };
