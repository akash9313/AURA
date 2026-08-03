import logging
from core.events import Event
from core.service import Service
from agent.orchestrator import AgentOrchestrator
from agent.state import WorkflowState

logger = logging.getLogger("AURA.AgentService")


class AgentService(Service):
    """
    AgentService connects the AgentOrchestrator engine to the AURA EventBus.
    """

    def __init__(self, bus, orchestrator: AgentOrchestrator = None):
        super().__init__(bus)
        self.orchestrator = orchestrator if orchestrator is not None else AgentOrchestrator(bus=bus)

    def start(self) -> None:
        logger.info("Agent Service Started")

        self.bus.subscribe(Event.GOAL_CREATED, self.on_goal_created)
        self.bus.subscribe(Event.INTENT_READY, self.on_intent_ready)

    def stop(self) -> None:
        logger.info("Agent Service Stopped")

    def on_goal_created(self, data: dict) -> None:
        goal = data.get("goal") if isinstance(data, dict) else str(data)
        if goal:
            wf = self.orchestrator.process_goal(goal)
            self._publish_summary(wf)

    def on_intent_ready(self, intent) -> None:
        # Route intent through AgentOrchestrator
        intent_name = getattr(intent, "name", "chat")
        params = getattr(intent, "parameters", {})

        if intent_name == "chat":
            goal = params.get("message", "Chat query")
        else:
            goal = f"Execute action '{intent_name}' with parameters {params}"

        logger.info(f"AgentService routing intent '{intent_name}' to AgentOrchestrator.")
        wf = self.orchestrator.process_goal(goal)
        self._publish_summary(wf)

    def _publish_summary(self, wf) -> None:
        # Extract output from tasks
        outputs = [t.result for t in wf.tasks if t.result is not None]
        if outputs:
            response_msg = str(outputs[-1])
        else:
            response_msg = f"Workflow {wf.workflow_id} ended with status: {wf.status.value}"

        self.bus.publish(Event.AI_RESPONSE_READY, response_msg)
