import logging
from typing import Any, Dict, Optional
from plugins.models import PluginPermission
from plugins.permissions import PluginPermissionValidator

logger = logging.getLogger("AURA.Plugins.Sandbox")


class PluginSandbox:
    """Enforces sandbox policy isolation based on granted permissions."""

    def __init__(self, permission_validator: PluginPermissionValidator):
        self.permission_validator = permission_validator

    def execute_in_sandbox(self, plugin_id: str, required_permission: Optional[PluginPermission], action_fn, *args, **kwargs) -> Any:
        if required_permission:
            if not self.permission_validator.check_permission(plugin_id, required_permission):
                raise PermissionError(f"Permission '{required_permission.value}' denied for plugin '{plugin_id}'.")

        return action_fn(*args, **kwargs)
