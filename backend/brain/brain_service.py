import logging
from core.service import Service
from core.models import Intent
from core.events import Event
from ai.intent_classifier import classify

logger = logging.getLogger("AURA.BrainService")


class BrainService(Service):

    def start(self) -> None:
        logger.info("Brain Service Started")
        self.bus.subscribe(
            Event.TEXT_READY,
            self.on_text_ready
        )

    def stop(self) -> None:
        logger.info("Brain Service Stopped")

    def on_text_ready(self, text: str) -> None:
        logger.info(f"Processing user text input: '{text}'")

        try:
            intent_data = classify(text)
            intent_name = intent_data.get("intent", "chat")
            intent_params = intent_data.get("parameters", {"message": text})

            intent = Intent(
                name=intent_name,
                parameters=intent_params,
                confidence=1.0
            )

            logger.info(f"Classified intent: '{intent_name}' with parameters {intent_params}")
            self.bus.publish(
                Event.INTENT_READY,
                intent
            )
        except Exception as e:
            logger.error(f"BrainService classification error for '{text}': {e}")
            # Fallback to chat intent
            fallback_intent = Intent(
                name="chat",
                parameters={"message": text},
                confidence=0.5
            )
            self.bus.publish(
                Event.INTENT_READY,
                fallback_intent
            )