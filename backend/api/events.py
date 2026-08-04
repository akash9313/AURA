from enum import Enum


class APIEvent(Enum):
    """Event definitions for AURA Platform API."""
    API_REQUEST = "api_request"
    API_RESPONSE = "api_response"
    WORKFLOW_STREAM = "workflow_stream"
    MEMORY_UPDATED = "memory_updated"
    PLUGIN_EVENT = "plugin_event"
    WEBHOOK_TRIGGERED = "webhook_triggered"
