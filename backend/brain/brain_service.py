from core.service import Service
from core.models import Intent
from core.events import Event
from ai.intent_classifier import classify


class BrainService(Service):

    def start(self):
        print("Brain Service Started")
        self.bus.subscribe(
            Event.TEXT_READY,
            self.on_text_ready
        )

    def stop(self):
        print("Brain Service Stopped")

    def on_text_ready(self, text):
        intent_data = classify(text)

        intent = Intent(
            name=intent_data["intent"],
            parameters=intent_data["parameters"],
            confidence=1.0
        )

        self.bus.publish(
            Event.INTENT_READY,
            intent
        )