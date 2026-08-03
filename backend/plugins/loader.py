import importlib.util
import logging
import os
from typing import Any
from plugins.models import PluginManifest

logger = logging.getLogger("AURA.Plugins.Loader")


class PluginLoader:
    """Dynamically loads plugin python modules."""

    def load_plugin(self, plugin_dir: str, manifest: PluginManifest) -> Any:
        main_file = os.path.join(plugin_dir, manifest.main_file)
        if not os.path.exists(main_file):
            raise FileNotFoundError(f"Plugin main file '{main_file}' not found.")

        spec = importlib.util.spec_from_file_location(f"aura_plugin_{manifest.id}", main_file)
        if spec is None or spec.loader is None:
            raise ImportError(f"Failed to create module spec for '{main_file}'")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        logger.info(f"Loaded module for plugin '{manifest.id}' from '{main_file}'")
        return module
