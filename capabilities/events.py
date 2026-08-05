from enum import Enum


class CapabilityEvent(Enum):
    CAPABILITY_REGISTERED = "capability_registered"
    CAPABILITY_UPDATED = "capability_updated"
    CAPABILITY_REMOVED = "capability_removed"
    CAPABILITY_SELECTED = "capability_selected"
