"""
UI Element Cache.
In-memory cache providing sub-100ms element retrieval with TTL expiration and intelligent invalidation.
"""

import logging
import time
from typing import Dict, Optional, Tuple

from computer.uia.configuration import UIAutomationConfig
from computer.uia.models import AURAUIElement

logger = logging.getLogger("AURA.Computer.UIA.Cache")


class UIElementCache:
    """
    LRU & TTL cache for AURAUIElement nodes.
    """

    def __init__(self, config: Optional[UIAutomationConfig] = None):
        self.config = config or UIAutomationConfig()
        self._cache: Dict[str, Tuple[AURAUIElement, float]] = {}

    def get(self, key: str) -> Optional[AURAUIElement]:
        """Retrieve cached element if not expired."""
        if not self.config.enable_smart_cache:
            return None

        if key in self._cache:
            elem, entry_time = self._cache[key]
            if time.time() - entry_time <= self.config.cache_ttl_seconds:
                logger.debug(f"Cache hit for key '{key}'")
                return elem

            # Expired
            del self._cache[key]
            logger.debug(f"Cache expired for key '{key}'")

        return None

    def put(self, key: str, element: AURAUIElement) -> None:
        """Store element in cache with current timestamp."""
        if not self.config.enable_smart_cache:
            return

        if len(self._cache) >= self.config.max_cached_elements:
            # Evict oldest entry
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][1])
            del self._cache[oldest_key]

        self._cache[key] = (element, time.time())
        logger.debug(f"Cached element under key '{key}'")

    def invalidate(self, key_prefix: Optional[str] = None) -> None:
        """Invalidate cache entries."""
        if key_prefix:
            keys_to_del = [k for k in self._cache if k.startswith(key_prefix)]
            for k in keys_to_del:
                del self._cache[k]
            logger.debug(f"Invalidated {len(keys_to_del)} cache entries matching prefix '{key_prefix}'")
        else:
            self._cache.clear()
            logger.debug("Cache cleared")
