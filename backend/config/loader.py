import json
import logging
import os
from typing import Dict, Any, Optional
from config.defaults import DEFAULT_CONFIG, DEFAULT_FEATURE_FLAGS
from config.environment import EnvironmentConfigLoader
from config.models import AppConfig, CategoryConfig, FeatureFlagState

logger = logging.getLogger("AURA.Config.Loader")


class ConfigLoader:
    """Hierarchical Configuration Loader."""

    def __init__(self):
        self.env_loader = EnvironmentConfigLoader()

    def load_config(self, config_filepath: Optional[str] = None) -> AppConfig:
        # 1. Base Defaults
        merged: Dict[str, Dict[str, Any]] = {cat: dict(settings) for cat, settings in DEFAULT_CONFIG.items()}

        # 2. File Config Overrides (JSON / YAML)
        if config_filepath and os.path.exists(config_filepath):
            try:
                with open(config_filepath, "r", encoding="utf-8") as f:
                    file_data = json.load(f)
                    for cat, settings in file_data.items():
                        if cat in merged and isinstance(settings, dict):
                            merged[cat].update(settings)
                        elif isinstance(settings, dict):
                            merged[cat] = settings
                logger.info(f"Loaded config overrides from file '{config_filepath}'")
            except Exception as e:
                logger.error(f"Error reading config file '{config_filepath}': {e}")

        # 3. Environment Variable Overrides
        env_overrides = self.env_loader.load_environment_overrides()
        for cat, settings in env_overrides.items():
            if cat in merged:
                merged[cat].update(settings)
            else:
                merged[cat] = settings

        # 4. Construct AppConfig
        categories = {cat: CategoryConfig(name=cat, settings=settings) for cat, settings in merged.items()}
        flags = {
            name: FeatureFlagState(name=name, enabled=meta["enabled"], description=meta.get("description", ""))
            for name, meta in DEFAULT_FEATURE_FLAGS.items()
        }

        return AppConfig(categories=categories, feature_flags=flags)
