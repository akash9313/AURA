from core.service import Service
from core.events import Event
from speech.providers.edge_provider import speak



class SpeechService(Service):

    def start(self):
        print("Speech Service Started")

        self.bus.subscribe(
            Event.AI_RESPONSE_READY,
            self.on_ai_response
        )

        self.bus.subscribe(
            Event.SHUTDOWN,
            self.on_shutdown
        )

    def on_ai_response(self, response):
        print(f"\n🤖 AURA: {response}")
        speak(response)

    def on_shutdown(self, _):
        print("\n👋 Goodbye from AURA!")
