import logging
from core.events import Event
from core.service import Service
from cognition.engine import CognitiveEngine

logger = logging.getLogger("AURA.CognitiveService")


class CognitiveService(Service):
    """
    CognitiveService connects CognitiveEngine reasoning to the AURA EventBus.
    """

    def __init__(self, bus, engine: CognitiveEngine = None):
        super().__init__(bus)
        self.engine = engine if engine is not None else CognitiveEngine(bus=bus)

    def start(self) -> None:
        logger.info("Cognitive Engine Service Started")
        self.bus.subscribe(Event.TEXT_READY, self.on_text_ready)

    def stop(self) -> None:
        logger.info("Cognitive Engine Service Stopped")

    def on_text_ready(self, text: str) -> None:
        """Handle incoming user text input through Cognitive Loop reasoning."""
        logger.info(f"CognitiveService processing user text: '{text}'")
        try:
            res = self.engine.process_request(text)
            answer = res.get("answer", "Goal processing completed.")
            self.bus.publish(Event.AI_RESPONSE_READY, answer)
        except Exception as e:
            logger.error(f"CognitiveService execution error: {e}")
            self.bus.publish(Event.AI_RESPONSE_READY, f"Cognitive processing error: {e}")
