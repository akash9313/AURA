import logging
from plugins.models import PluginState, PluginStatus

logger = logging.getLogger("AURA.Plugins.Lifecycle")


class PluginLifecycleManager:
    """Governs plugin state transitions (INSTALL -> VALIDATE -> LOAD -> ENABLE -> DISABLE -> UNLOAD -> REMOVE)."""

    def transition(self, status: PluginStatus, target_state: PluginState) -> PluginStatus:
        logger.info(f"Transitioning plugin '{status.plugin_id}' from '{status.state.value}' -> '{target_state.value}'")
        status.state = target_state
        return status
