import logging
from plugins.installer import PluginInstaller

logger = logging.getLogger("AURA.Plugins.Updater")


class PluginUpdater:
    """Handles semantic version upgrades for installed plugins."""

    def __init__(self, installer: PluginInstaller):
        self.installer = installer

    def update_plugin(self, source_dir: str):
        return self.installer.install_plugin_directory(source_dir)
