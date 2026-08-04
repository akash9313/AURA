import logging
from core.events import Event
from core.service import Service
from skills.composer import SkillComposer
from skills.events import SkillEvent
from skills.executor import SkillExecutor
from skills.marketplace import SkillMarketplace
from skills.registry import SkillRegistry

logger = logging.getLogger("AURA.Skills.Service")


class SkillService(Service):
    """
    Cognitive Skill Service wrapper connecting SkillRegistry, SkillExecutor, SkillComposer, and Marketplace to EventBus.
    """

    def __init__(self, bus):
        super().__init__(bus)
        self.registry = SkillRegistry()
        self.composer = SkillComposer(self.registry)
        self.marketplace = SkillMarketplace(self.registry)
        self.executor = SkillExecutor(self.registry)

    def start(self):
        logger.info("Cognitive Skills Service Started.")
        if self.bus:
            self.bus.subscribe(Event.GOAL_CREATED, self.on_goal_created)

    def on_goal_created(self, payload):
        goal = payload.get("goal", "").lower()
        if "skill" in goal:
            logger.info("Cognitive Skills Service processing skill goal.")
