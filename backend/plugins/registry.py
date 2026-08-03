import logging
from typing import Dict, List, Optional
from plugins.models import PluginStatus

logger = logging.getLogger("AURA.Plugins.Registry")


class PluginRegistry:
    """Registry tracking installed and loaded plugins."""

    def __init__(self):
        self.plugins: Dict[str, PluginStatus] = {}

    def register_plugin(self, status: PluginStatus) -> None:
        self.plugins[status.plugin_id] = status
        logger.info(f"Registered plugin '{status.plugin_id}' [{status.state.value}]")

    def unregister_plugin(self, plugin_id: str) -> Optional[PluginStatus]:
        status = self.plugins.pop(plugin_id, None)
        if status:
            logger.info(f"Unregistered plugin '{plugin_id}'")
        return status

    def get_plugin(self, plugin_id: str) -> Optional[PluginStatus]:
        return self.plugins.get(plugin_id)

    def list_plugins(self) -> List[PluginStatus]:
        return list(self.plugins.values())

