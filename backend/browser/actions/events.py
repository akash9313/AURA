"""
Browser Action Engine Event Definitions.
Published to the AURA EventBus during action execution, element lookup, form submission, and downloads.
"""

from enum import Enum


class ActionEvent(Enum):
    """Event definitions for Browser Action Engine."""
    ACTION_STARTED = "action_started"
    ACTION_COMPLETED = "action_completed"
    ACTION_FAILED = "action_failed"
    ELEMENT_FOUND = "element_found"
    ELEMENT_NOT_FOUND = "element_not_found"
    FORM_SUBMITTED = "form_submitted"
    DOWNLOAD_STARTED = "download_started"
    DOWNLOAD_COMPLETED = "download_completed"
