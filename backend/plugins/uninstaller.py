import logging
import os
import shutil

logger = logging.getLogger("AURA.Plugins.Uninstaller")


class PluginUninstaller:
    """Uninstalls and removes plugin files."""

    def __init__(self, target_plugins_dir: str):
        self.target_dir = target_plugins_dir

    def uninstall_plugin(self, plugin_id: str) -> bool:
        dest_dir = os.path.join(self.target_dir, plugin_id)
        if os.path.exists(dest_dir):
            shutil.rmtree(dest_dir)
            logger.info(f"Uninstalled plugin directory '{dest_dir}'")
            return True
        return False
