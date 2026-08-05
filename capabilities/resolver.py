import logging
from typing import Optional

from capabilities.configuration import CapabilityConfig
from capabilities.models import Capability
from capabilities.registry import CapabilityRegistry

logger = logging.getLogger("AURA.Capabilities.Resolver")


class CapabilityResolver:
    def __init__(self, registry: CapabilityRegistry, config: Optional[CapabilityConfig] = None):
        self.registry = registry
        self.config = config or CapabilityConfig()

    def resolve(self, capability_id_or_alias: str) -> Optional[Capability]:
        cap = self.registry.get(capability_id_or_alias)
        if not cap:
            return None

        if not cap.enabled:
            return None

        if cap.is_experimental and not self.config.enable_experimental:
            return None

        if cap.is_deprecated:
            if cap.replaced_by:
                replacement = self.registry.get(cap.replaced_by)
                if replacement and replacement.enabled:
                    return replacement

        if self.config.platform_filter:
            if self.config.platform_filter.lower() not in [p.lower() for p in cap.supported_platforms]:
                return None

        return cap
