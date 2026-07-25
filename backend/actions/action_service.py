from core.service import Service
from core.events import Event


class ActionService(Service):

    def start(self):

        print("Action Service Started")

        self.bus.subscribe(
            Event.INTENT_READY,
            self.on_action
        )

        self.bus.subscribe(
            Event.ACTION_READY,
            self.on_action
        )

    def stop(self):

        print("Action Service Stopped")

    def on_action(self, intent):

        print(f"⚙️ Action: {intent.name}")

        if intent.name == "chat":

            # Existing Gemini call
            from ai.llm import ask_ai

            response = ask_ai(
                intent.parameters["message"]
            )

        elif intent.name == "open_application":

            response = (
                f"I would open "
                f"{intent.parameters['application']} here."
            )

        else:

            response = (
                "I don't know how to do that yet."
            )

        self.bus.publish(
            Event.AI_RESPONSE_READY,
            response
        )