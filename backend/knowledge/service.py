import logging
from core.events import Event
from core.service import Service
from knowledge.events import KnowledgeEvent
from knowledge.manager import KnowledgeManager

logger = logging.getLogger("AURA.Knowledge.Service")


class KnowledgeService(Service):
    """
    Knowledge Service wrapper connecting KnowledgeManager to EventBus.
    """

    def __init__(self, bus):
        super().__init__(bus)
        self.manager = KnowledgeManager()

    def start(self):
        logger.info("Knowledge Service Started.")
        if self.bus:
            self.bus.subscribe(Event.GOAL_CREATED, self.on_goal_created)

    def on_goal_created(self, payload):
        goal = payload.get("goal", "").lower()
        if "import" in goal or "search" in goal:
            logger.info("Knowledge Service processing knowledge goal.")
