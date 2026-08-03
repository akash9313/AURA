import logging
from computer.controller import ComputerController
from computer.events import ComputerEvent
from core.events import Event
from core.service import Service

logger = logging.getLogger("AURA.Computer.Service")


class ComputerUseService(Service):
    """
    Computer Use Service wrapper connecting ComputerController to EventBus.
    """

    def __init__(self, bus):
        super().__init__(bus)
        self.controller = ComputerController()

    def start(self):
        logger.info("Computer Use Service Started.")
        if self.bus:
            self.bus.subscribe(Event.SHORTCUT_EXECUTED, self.on_shortcut_executed)
            self.bus.subscribe(Event.TEXT_TYPED, self.on_text_typed)

    def on_shortcut_executed(self, payload):
        keys = payload.get("keys", [])
        if keys:
            self.controller.press_shortcut(keys)

    def on_text_typed(self, payload):
        text = payload.get("text", "")
        if text:
            self.controller.type_text(text)
