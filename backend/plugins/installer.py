import logging
import os
import shutil
from typing import Optional
from plugins.manifest import ManifestParser
from plugins.models import PluginManifest, PluginState, PluginStatus
from plugins.validator import PluginValidator

logger = logging.getLogger("AURA.Plugins.Installer")


class PluginInstaller:
    """Installs plugin packages and unpacks plugin directories."""

    def __init__(self, target_plugins_dir: str):
        self.target_dir = target_plugins_dir
        self.parser = ManifestParser()
        self.validator = PluginValidator()
        os.makedirs(self.target_dir, exist_ok=True)

    def install_plugin_directory(self, source_dir: str) -> PluginStatus:
        manifest_file = os.path.join(source_dir, "manifest.json")
        manifest = self.parser.parse_manifest_file(manifest_file)
        self.validator.validate_manifest(manifest)

        dest_dir = os.path.join(self.target_dir, manifest.id)
        if os.path.exists(dest_dir):
            shutil.rmtree(dest_dir)

        shutil.copytree(source_dir, dest_dir)
        logger.info(f"Installed plugin '{manifest.id}' to '{dest_dir}'")

        return PluginStatus(plugin_id=manifest.id, state=PluginState.INSTALLED, manifest=manifest)
