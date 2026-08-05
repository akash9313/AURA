import asyncio
import logging
from typing import Any, Dict, Optional

from core.service import Service
from workflow.integration.configuration import WorkflowIntegrationConfig
from workflow.integration.execution_coordinator import ExecutionCoordinator
from workflow.integration.models import MissionExecutionResult, MissionExecutionStatus
from workflow.integration.progress_reporter import ProgressReporter
from workflow.integration.result_formatter import ResultFormatter

logger = logging.getLogger("AURA.Workflow.Integration.Service")


class WorkflowExecutorIntegrationService(Service):
    def __init__(
        self,
        bus: Any = None,
        config: Optional[WorkflowIntegrationConfig] = None,
        coordinator: Optional[ExecutionCoordinator] = None,
    ):
        super().__init__(bus)
        self.config = config or WorkflowIntegrationConfig()
        self.reporter = ProgressReporter(bus=bus)
        self.coordinator = coordinator or ExecutionCoordinator(
            config=self.config,
            reporter=self.reporter,
        )
        self.result_formatter = ResultFormatter()

    def start(self) -> None:
        if self.bus:
            self.bus.subscribe("MISSION_EXECUTION_REQUESTED", self._on_execution_requested)
            self.bus.subscribe("workflow_execution_requested", self._on_execution_requested)

    def stop(self) -> None:
        self.cancel_current_execution("Service stopped")

    def is_healthy(self) -> bool:
        return True

    def cancel_current_execution(self, reason: str = "User cancelled") -> None:
        if self.coordinator:
            self.coordinator.cancel(reason)

    def _on_execution_requested(self, payload: Any) -> None:
        if isinstance(payload, dict):
            mission_id = payload.get("mission_id", "msn_unknown")
            plan_obj = payload.get("plan")
            task_graph = getattr(plan_obj, "task_graph", None) if plan_obj else payload.get("task_graph")

            if task_graph:
                try:
                    loop = asyncio.get_running_loop()
                    loop.create_task(self.execute_mission(mission_id, task_graph))
                except RuntimeError:
                    asyncio.run(self.execute_mission(mission_id, task_graph))

    async def execute_mission(self, mission_id: str, task_graph: Any) -> MissionExecutionResult:
        result = await self.coordinator.execute_mission_plan(mission_id, task_graph)
        summary_text = self.result_formatter.format_summary(result)
        result.summary = summary_text

        if self.bus:
            self.bus.publish("ai_response_ready", {"text": summary_text})
            self.bus.publish("workflow_completed", result.to_dict())

        return result
