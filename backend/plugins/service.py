import logging
from core.events import Event
from core.service import Service
from plugins.events import PluginEvent
from plugins.manager import PluginManager

logger = logging.getLogger("AURA.Plugins.Service")


class PluginService(Service):
    """
    Plugin Service wrapper connecting PluginManager to EventBus.
    """

    def __init__(self, bus):
        super().__init__(bus)
        self.manager = PluginManager()

    def start(self):
        logger.info("Plugin Service Started.")
        if self.bus:
            self.bus.subscribe(Event.GOAL_CREATED, self.on_goal_created)

    def on_goal_created(self, payload):
        goal = payload.get("goal", "").lower()
        if "plugin" in goal:
            logger.info("Plugin Service processing plugin goal.")
