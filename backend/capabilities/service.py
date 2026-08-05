"""
Capability Registry Service.
Top-level AURA service integrating the Capability Registry Engine into the kernel framework.
Acts as single source of truth describing everything AURA can do.
"""

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
    """
    Service wrapper exposing Capability Registry capabilities to AURA Runtime, AI Planner, and Workflow Engine.
    """

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

        # Auto-load builtins
        self.loader.load_builtins()
        logger.info("CapabilityService initialized")

    def register_capability(self, capability: Capability) -> bool:
        """Register capability."""
        return self.registry.register(capability)

    def unregister_capability(self, capability_id: str) -> bool:
        """Unregister capability."""
        return self.registry.unregister(capability_id)

    def get_capability(self, capability_id_or_alias: str) -> Optional[Capability]:
        """Resolve capability by ID or alias."""
        return self.resolver.resolve(capability_id_or_alias)

    def match_capabilities(self, request_intent: str) -> List[CapabilityMatchResult]:
        """Match and rank capabilities for request intent."""
        return self.matcher.match(request_intent)

    def find_best_capability(self, request_intent: str) -> Optional[CapabilityMatchResult]:
        """Find single best matching capability."""
        return self.matcher.find_best_capability(request_intent)

    def list_capabilities(self, category: Optional[CapabilityCategory] = None) -> List[Capability]:
        """List all capabilities."""
        return self.registry.list_all(category)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        logger.info("Starting CapabilityService...")

    def stop(self) -> None:
        logger.info("Stopping CapabilityService...")

    def is_healthy(self) -> bool:
        return True
