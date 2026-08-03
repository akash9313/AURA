import json
import logging
import os
from typing import Dict, Any
from plugins.models import PluginManifest, PluginPermission

logger = logging.getLogger("AURA.Plugins.Manifest")


class ManifestParser:
    """Parses and validates plugin manifest.json files."""

    def parse_manifest_file(self, manifest_path: str) -> PluginManifest:
        if not os.path.exists(manifest_path):
            raise FileNotFoundError(f"Plugin manifest file '{manifest_path}' not found.")

        with open(manifest_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)

        perms = []
        for p_str in data.get("permissions", []):
            try:
                perms.append(PluginPermission(p_str.lower()))
            except ValueError:
                logger.warning(f"Ignoring unknown permission '{p_str}' in manifest '{manifest_path}'")

        manifest = PluginManifest(
            id=data.get("id", ""),
            name=data.get("name", ""),
            version=data.get("version", "1.0.0"),
            description=data.get("description", ""),
            author=data.get("author", "Unknown"),
            main_file=data.get("main", "index.py"),
            permissions=perms,
            commands=data.get("commands", []),
            tools=data.get("tools", [])
        )
        return manifest
