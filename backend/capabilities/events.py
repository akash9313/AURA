"""
Capability Event Definitions.
Published to AURA EventBus during capability registration, updates, removal, and selection.
"""

from enum import Enum


class CapabilityEvent(Enum):
    """Event definitions for Capability Registry Engine."""
    CAPABILITY_REGISTERED = "capability_registered"
    CAPABILITY_UPDATED = "capability_updated"
    CAPABILITY_REMOVED = "capability_removed"
    CAPABILITY_SELECTED = "capability_selected"
