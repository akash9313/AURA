import logging
import threading
from typing import Dict, List, Optional
from config.defaults import DEFAULT_FEATURE_FLAGS
from config.models import FeatureFlagState

logger = logging.getLogger("AURA.Config.FeatureFlags")


class FeatureFlagManager:
    """
    Feature Flag Manager.
    Allows runtime enablement and safe rollout of experimental system capabilities.
    """

    def __init__(self, bus=None, initial_flags: Optional[Dict[str, FeatureFlagState]] = None):
        self.bus = bus
        self._flags: Dict[str, FeatureFlagState] = {}
        self._lock = threading.Lock()

        # Load defaults
        for name, meta in DEFAULT_FEATURE_FLAGS.items():
            self._flags[name] = FeatureFlagState(
                name=name,
                enabled=meta["enabled"],
                description=meta.get("description", "")
            )

        if initial_flags:
            self._flags.update(initial_flags)

    def is_enabled(self, name: str) -> bool:
        with self._lock:
            flag = self._flags.get(name)
            return flag.enabled if flag else False

    def set_flag(self, name: str, enabled: bool) -> None:
        with self._lock:
            if name in self._flags:
                self._flags[name].enabled = enabled
            else:
                self._flags[name] = FeatureFlagState(name=name, enabled=enabled)

        logger.info(f"Feature Flag updated: '{name}' -> Enabled={enabled}")

        if self.bus:
            evt = "feature_enabled" if enabled else "feature_disabled"
            self.bus.publish(evt, {"feature_name": name, "enabled": enabled})

    def get_all_flags(self) -> List[FeatureFlagState]:
        with self._lock:
            return list(self._flags.values())
