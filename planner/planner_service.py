from core.service import Service
from core.events import Event


class PlannerService(Service):

    def start(self):
        print("Planner Service Started")

        self.bus.subscribe(
            Event.INTENT_READY,
            self.on_intent
        )

    def stop(self):
        print("Planner Service Stopped")

    def on_intent(self, intent):

        print(f"📋 Planner received: {intent}")

        self.bus.publish(
            Event.ACTION_READY,
            intent
        )