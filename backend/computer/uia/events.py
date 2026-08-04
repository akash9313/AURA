"""
UI Automation Event Definitions.
Emitted to AURA EventBus during UI element discovery, action execution, and tree mutations.
"""

from enum import Enum


class UIAutomationEvent(Enum):
    """Event definitions for UI Automation Engine."""
    CONTROL_FOUND = "control_found"
    CONTROL_NOT_FOUND = "control_not_found"
    CONTROL_CLICKED = "control_clicked"
    TEXT_ENTERED = "text_entered"
    VALUE_CHANGED = "value_changed"
    CONTROL_EXPANDED = "control_expanded"
    CONTROL_COLLAPSED = "control_collapsed"
    AUTOMATION_TREE_UPDATED = "automation_tree_updated"
