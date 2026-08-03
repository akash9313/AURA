import logging
from typing import Dict, Set
from plugins.models import PluginManifest, PluginPermission

logger = logging.getLogger("AURA.Plugins.Permissions")


class PluginPermissionValidator:
    """Manages and checks plugin resource permissions."""

    def __init__(self):
        self.granted_permissions: Dict[str, Set[PluginPermission]] = {}

    def grant_permissions(self, plugin_id: str, permissions: Set[PluginPermission]) -> None:
        self.granted_permissions[plugin_id] = permissions
        logger.info(f"Granted permissions for plugin '{plugin_id}': {[p.value for p in permissions]}")

    def check_permission(self, plugin_id: str, permission: PluginPermission) -> bool:
        granted = self.granted_permissions.get(plugin_id, set())
        has_perm = permission in granted
        if not has_perm:
            logger.warning(f"Permission denied: Plugin '{plugin_id}' attempted to access '{permission.value}' without explicit grant.")
        return has_perm
