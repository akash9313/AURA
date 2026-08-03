from enum import Enum


class PluginEvent(Enum):
    """Event definitions for Plugin Platform."""
    PLUGIN_INSTALLED = "plugin_installed"
    PLUGIN_UPDATED = "plugin_updated"
    PLUGIN_ENABLED = "plugin_enabled"
    PLUGIN_DISABLED = "plugin_disabled"
    PLUGIN_REMOVED = "plugin_removed"
    PLUGIN_ERROR = "plugin_error"
