import logging
from typing import Any, List, Optional

from capabilities.configuration import CapabilityConfig
from capabilities.loader import CapabilityLoader
from capabilities.matcher import CapabilityMatcher
from capabilities.models import Capability, CapabilityCategory, CapabilityMatchResult
from capabilities.registry import CapabilityRegistry
from capabilities.resolver import CapabilityResolver
from core.service import Service

logger = logging.getLogger("AURA.Capabilities.Service")


class CapabilityService(Service):
    def __init__(
        self,
        bus: Any = None,
        config: Optional[CapabilityConfig] = None,
    ):
        super().__init__(bus)
        self.config = config or CapabilityConfig()
        self.registry = CapabilityRegistry(bus=bus)
        self.resolver = CapabilityResolver(self.registry, self.config)
        self.matcher = CapabilityMatcher(self.registry, self.config)
        self.loader = CapabilityLoader(self.registry)

        self.loader.load_builtins()

    def register_capability(self, capability: Capability) -> bool:
        return self.registry.register(capability)

    def unregister_capability(self, capability_id: str) -> bool:
        return self.registry.unregister(capability_id)

    def get_capability(self, capability_id_or_alias: str) -> Optional[Capability]:
        return self.resolver.resolve(capability_id_or_alias)

    def match_capabilities(self, request_intent: str) -> List[CapabilityMatchResult]:
        return self.matcher.match(request_intent)

    def find_best_capability(self, request_intent: str) -> Optional[CapabilityMatchResult]:
        return self.matcher.find_best_capability(request_intent)

    def list_capabilities(self, category: Optional[CapabilityCategory] = None) -> List[Capability]:
        return self.registry.list_all(category)

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def is_healthy(self) -> bool:
        return True
