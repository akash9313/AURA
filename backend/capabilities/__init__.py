"""
AURA Capability Registry Subsystem (`backend/capabilities/`).
Single source of truth describing everything AURA can do. Enables Planner to depend strictly on capability abstractions rather than concrete implementations.
"""

from capabilities.configuration import CapabilityConfig
from capabilities.events import CapabilityEvent
from capabilities.loader import CapabilityLoader
from capabilities.matcher import CapabilityMatcher
from capabilities.models import (
    Capability,
    CapabilityCategory,
    CapabilityMatchResult,
)
from capabilities.registry import CapabilityRegistry
from capabilities.resolver import CapabilityResolver
from capabilities.service import CapabilityService
from capabilities.validator import CapabilityValidator

__all__ = [
    "CapabilityService",
    "CapabilityRegistry",
    "CapabilityResolver",
    "CapabilityMatcher",
    "CapabilityLoader",
    "CapabilityValidator",
    "CapabilityConfig",
    "Capability",
    "CapabilityCategory",
    "CapabilityMatchResult",
    "CapabilityEvent",
]
