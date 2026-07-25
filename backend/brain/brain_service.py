from core.service import Service
from core.models import Intent
from core.events import Event


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
        text_lower = text.lower()

        if "open chrome" in text_lower:
            intent = Intent(
                name="open_application",
                parameters={
                    "application": "chrome"
                },
                confidence=0.99
            )
        else:
            intent = Intent(
                name="chat",
                parameters={
                    "message": text
                },
                confidence=1.0
            )

        self.bus.publish(
            Event.INTENT_READY,
            intent
        )