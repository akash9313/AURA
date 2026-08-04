import logging
import time
from typing import Dict, Optional, Tuple

from computer.uia.configuration import UIAutomationConfig
from computer.uia.models import AURAUIElement

logger = logging.getLogger("AURA.Computer.UIA.Cache")


class UIElementCache:
    def __init__(self, config: Optional[UIAutomationConfig] = None):
        self.config = config or UIAutomationConfig()
        self._cache: Dict[str, Tuple[AURAUIElement, float]] = {}

    def get(self, key: str) -> Optional[AURAUIElement]:
        if not self.config.enable_smart_cache:
            return None

        if key in self._cache:
            elem, entry_time = self._cache[key]
            if time.time() - entry_time <= self.config.cache_ttl_seconds:
                return elem
            del self._cache[key]

        return None

    def put(self, key: str, element: AURAUIElement) -> None:
        if not self.config.enable_smart_cache:
            return

        if len(self._cache) >= self.config.max_cached_elements:
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][1])
            del self._cache[oldest_key]

        self._cache[key] = (element, time.time())

    def invalidate(self, key_prefix: Optional[str] = None) -> None:
        if key_prefix:
            keys_to_del = [k for k in self._cache if k.startswith(key_prefix)]
            for k in keys_to_del:
                del self._cache[k]
        else:
            self._cache.clear()
