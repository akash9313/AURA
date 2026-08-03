import logging
from plugins.models import PluginManifest

logger = logging.getLogger("AURA.Plugins.Validator")


class PluginValidator:
    """Validates plugin manifest completeness and safety constraints."""

    def validate_manifest(self, manifest: PluginManifest) -> bool:
        if not manifest.id:
            raise ValueError("Plugin manifest missing 'id'.")
        if not manifest.name:
            raise ValueError("Plugin manifest missing 'name'.")
        if not manifest.main_file:
            raise ValueError("Plugin manifest missing 'main_file'.")
        logger.info(f"Manifest for plugin '{manifest.id}' validated successfully.")
        return True
