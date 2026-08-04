"""
Application Subsystem Event Definitions.
Published to AURA EventBus during application lifecycle events, readiness state updates, and resource monitoring.
"""

from enum import Enum


class ApplicationEvent(Enum):
    """Event definitions for Application Manager Subsystem."""
    APPLICATION_LAUNCHED = "application_launched"
    APPLICATION_READY = "application_ready"
    APPLICATION_CLOSED = "application_closed"
    APPLICATION_CRASHED = "application_crashed"
    APPLICATION_RESTARTED = "application_restarted"
    APPLICATION_NOT_FOUND = "application_not_found"
    RESOURCE_UPDATED = "resource_updated"
