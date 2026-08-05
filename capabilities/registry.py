import json
import logging
import threading
from typing import Any, Dict, List, Optional

from capabilities.events import CapabilityEvent
from capabilities.models import Capability, CapabilityCategory
from capabilities.validator import CapabilityValidator

logger = logging.getLogger("AURA.Capabilities.Registry")


class CapabilityRegistry:
    def __init__(self, bus: Any = None):
        self.bus = bus
        self._capabilities: Dict[str, Capability] = {}
        self._alias_map: Dict[str, str] = {}
        self._lock = threading.RLock()
        self.validator = CapabilityValidator()

    def register(self, capability: Capability) -> bool:
        is_valid, errors = self.validator.validate_capability(capability)
        if not is_valid:
            return False

        with self._lock:
            cid = capability.capability_id
            is_update = cid in self._capabilities
            self._capabilities[cid] = capability

            for alias in capability.aliases:
                self._alias_map[alias.lower()] = cid

            evt = CapabilityEvent.CAPABILITY_UPDATED if is_update else CapabilityEvent.CAPABILITY_REGISTERED
            self._publish_event(evt, capability.to_dict())
            return True

    def unregister(self, capability_id: str) -> bool:
        with self._lock:
            if capability_id in self._capabilities:
                cap = self._capabilities.pop(capability_id)
                for alias in cap.aliases:
                    if alias.lower() in self._alias_map:
                        del self._alias_map[alias.lower()]
                self._publish_event(CapabilityEvent.CAPABILITY_REMOVED, {"capability_id": capability_id})
                return True
            return False

    def get(self, capability_id_or_alias: str) -> Optional[Capability]:
        with self._lock:
            key = capability_id_or_alias
            if key in self._capabilities:
                return self._capabilities[key]
            target_id = self._alias_map.get(key.lower())
            if target_id and target_id in self._capabilities:
                return self._capabilities[target_id]
            return None

    def list_all(self, category: Optional[CapabilityCategory] = None) -> List[Capability]:
        with self._lock:
            caps = list(self._capabilities.values())
            if category:
                caps = [c for c in caps if c.category == category]
            return caps

    def to_json(self) -> str:
        with self._lock:
            data = [cap.to_dict() for cap in self._capabilities.values()]
            return json.dumps(data, indent=2)

    def _publish_event(self, event: CapabilityEvent, data: Dict[str, Any]) -> None:
        if self.bus:
            try:
                self.bus.publish(event.value, data)
            except Exception as e:
                logger.error(f"Failed to publish capability event '{event.value}': {e}")
