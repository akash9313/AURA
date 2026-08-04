import logging
from typing import Any, List, Optional
from core.service import Service
from config.feature_flags import FeatureFlagManager
from config.loader import ConfigLoader
from config.models import AppConfig
from config.validator import ConfigValidator

logger = logging.getLogger("AURA.Config.Service")


class ConfigService(Service):
    """
    Centralized Configuration & Feature Flag Service.
    Serves as the single source of truth for all runtime settings across AURA.
    Supports hot-reloading and schema validation.
    """

    def __init__(self, bus, config_filepath: Optional[str] = None):
        super().__init__(bus)
        self.config_filepath = config_filepath
        self.loader = ConfigLoader()
        self.validator = ConfigValidator()
        self.app_config: AppConfig = self.loader.load_config(self.config_filepath)
        self.flag_manager = FeatureFlagManager(bus=bus, initial_flags=self.app_config.feature_flags)

    def start(self):
        logger.info("Centralized Configuration & Feature Flag Service Started.")
        valid, errors = self.validator.validate(self.app_config)
        if valid and self.bus:
            self.bus.publish("config_loaded", {"environment": self.app_config.environment})
        elif not valid and self.bus:
            self.bus.publish("config_validation_failed", {"errors": errors})

    def stop(self):
        logger.info("Configuration Service Stopped.")

    def get(self, category: str, key: str, default: Any = None) -> Any:
        return self.app_config.get(category, key, default)

    def is_feature_enabled(self, feature_name: str) -> bool:
        return self.flag_manager.is_enabled(feature_name)

    def set_feature_flag(self, feature_name: str, enabled: bool) -> None:
        self.flag_manager.set_flag(feature_name, enabled)

    def reload_config(self) -> AppConfig:
        """Hot-reload configuration from source files and environment overrides."""

        logger.info("Reloading Configuration...")
        new_config = self.loader.load_config(self.config_filepath)
        valid, errors = self.validator.validate(new_config)

        if valid:
            self.app_config = new_config
            logger.info("Configuration Reloaded Successfully.")
            if self.bus:
                self.bus.publish("config_reloaded", {"environment": self.app_config.environment})
        else:
            logger.warning("Configuration reload rejected due to validation errors.")
            if self.bus:
                self.bus.publish("config_validation_failed", {"errors": errors})

        return self.app_config
