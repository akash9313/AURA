import logging
from api.events import APIEvent
from api.gateway import APIGateway
from core.events import Event
from core.service import Service

logger = logging.getLogger("AURA.API.Service")


class APIService(Service):
    """
    API Service wrapper connecting APIGateway to EventBus.
    """

    def __init__(self, bus):
        super().__init__(bus)
        self.gateway = APIGateway(bus=bus)

    def start(self):
        logger.info("Platform API Gateway Service Started.")
        if self.bus:
            self.bus.subscribe(Event.GOAL_CREATED, self.on_goal_created)

    def on_goal_created(self, payload):
        goal = payload.get("goal", "").lower()
        if "api" in goal:
            logger.info("API Service processing platform API goal.")
