import logging
from core.events import Event
from core.service import Service
from learning.engine import AdaptiveIntelligenceEngine
from learning.events import LearningEvent

logger = logging.getLogger("AURA.Learning.Service")


class LearningService(Service):
    """
    Learning Service wrapper connecting AdaptiveIntelligenceEngine to EventBus.
    """

    def __init__(self, bus):
        super().__init__(bus)
        self.engine = AdaptiveIntelligenceEngine(bus=bus)

    def start(self):
        logger.info("Adaptive Intelligence Service Started.")
        if self.bus:
            self.bus.subscribe(Event.WORKFLOW_COMPLETED, self.on_workflow_completed)
            self.bus.subscribe(Event.APPLICATION_OPENED, self.on_application_opened)

    def on_workflow_completed(self, payload):
        goal = payload.get("goal", "")
        status = payload.get("status", "")
        tasks = payload.get("completed_tasks", [])
        seq = [t.get("tool", "") for t in tasks if t.get("tool")]
        if goal:
            self.engine.process_workflow_outcome(goal, seq, success=(status == "completed"))
            if self.bus:
                self.bus.publish(LearningEvent.LEARNING_COMPLETED.value, {"goal": goal})

    def on_application_opened(self, payload):
        app_name = payload.get("app_name", "")
        if app_name:
            self.engine.preferences.infer_preference_from_action("open_app", app_name)
