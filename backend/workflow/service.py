import logging
from core.events import Event
from core.service import Service
from workflow.engine import WorkflowEngine
from workflow.events import WorkflowEvent

logger = logging.getLogger("AURA.Workflow.Service")


class WorkflowService(Service):
    """
    Workflow Service wrapper connecting WorkflowEngine to EventBus.
    """

    def __init__(self, bus):
        super().__init__(bus)
        self.engine = WorkflowEngine(bus=bus)

    def start(self):
        logger.info("Workflow Service Started.")
        if self.bus:
            self.bus.subscribe(Event.GOAL_CREATED, self.on_goal_created)

    def on_goal_created(self, payload):
        goal = payload.get("goal", "")
        if goal:
            report = self.engine.run_mission(goal)
            if self.bus:
                self.bus.publish(Event.WORKFLOW_COMPLETED.value, report)
