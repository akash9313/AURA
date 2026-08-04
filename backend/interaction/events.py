"""
Interaction Engine Event Definitions.
Published to AURA EventBus during strategy selection, method execution, fallbacks, and completion.
"""

from enum import Enum


class InteractionEvent(Enum):
    """Event definitions for Interaction Engine Subsystem."""
    INTERACTION_STARTED = "interaction_started"
    METHOD_SELECTED = "method_selected"
    METHOD_FAILED = "method_failed"
    METHOD_SWITCHED = "method_switched"
    INTERACTION_COMPLETED = "interaction_completed"
