import os
import tempfile
import unittest
from core.event_bus import EventBus
from config.environment import EnvironmentConfigLoader
from config.feature_flags import FeatureFlagManager
from config.loader import ConfigLoader
from config.models import AppConfig
from config.service import ConfigService
from config.validator import ConfigValidator


class TestConfigFeatureFlags(unittest.TestCase):

    def setUp(self):
        self.bus = EventBus()
        self.loader = ConfigLoader()
        self.validator = ConfigValidator()
        self.flag_mgr = FeatureFlagManager(bus=self.bus)
        self.service = ConfigService(bus=self.bus)

    def test_default_config_loading(self):
        """Test default configuration categories and settings."""
        self.assertEqual(self.service.get("stt", "model_name"), "base")
        self.assertEqual(self.service.get("llm", "temperature"), 0.7)
        self.assertEqual(self.service.get("tts", "volume"), 1.0)

    def test_feature_flag_management(self):
        """Test feature flag enablement, disablement, and event emission."""
        self.assertTrue(self.flag_mgr.is_enabled("streaming_voice"))

        events = []
        self.bus.subscribe("feature_disabled", lambda p: events.append(p))

        self.flag_mgr.set_flag("streaming_voice", False)
        self.assertFalse(self.flag_mgr.is_enabled("streaming_voice"))
        self.assertEqual(len(events), 1)

    def test_environment_variable_overrides(self):
        """Test loading AURA_* environment variable overrides."""
        os.environ["AURA_STT_MODEL_NAME"] = "large-v3"
        os.environ["AURA_LLM_TEMPERATURE"] = "0.2"

        env_loader = EnvironmentConfigLoader()
        overrides = env_loader.load_environment_overrides()

        self.assertEqual(overrides["stt"]["model_name"], "large-v3")
        self.assertEqual(overrides["llm"]["temperature"], 0.2)

        # Cleanup
        del os.environ["AURA_STT_MODEL_NAME"]
        del os.environ["AURA_LLM_TEMPERATURE"]

    def test_config_validator(self):
        """Test schema validation for types and ranges."""
        config = self.loader.load_config()
        valid, errors = self.validator.validate(config)
        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)

        # Introduce invalid temperature
        config.categories["llm"].settings["temperature"] = 5.0
        valid_bad, errors_bad = self.validator.validate(config)
        self.assertFalse(valid_bad)
        self.assertGreater(len(errors_bad), 0)

    def test_hot_reload_config(self):
        """Test runtime hot reloading."""
        self.service.start()
        reloaded = self.service.reload_config()
        self.assertIsNotNone(reloaded)


if __name__ == "__main__":
    unittest.main()
