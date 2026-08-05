"""
Workflow Executor Integration Service.
Top-level AURA service integrating Workflow Execution Engine into EventBus and Conversation Manager lifecycle.
Orchestrates capability execution, progress reporting, empirical verification, recovery, and final result reporting.
"""

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
    """
    Service wrapper connecting Workflow Execution Engine Integration to AURA EventBus.
    """

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

        logger.info("WorkflowExecutorIntegrationService initialized")

    def start(self) -> None:
        """Start service and subscribe to EventBus execution channels."""
        logger.info("Starting WorkflowExecutorIntegrationService...")
        if self.bus:
            self.bus.subscribe("MISSION_EXECUTION_REQUESTED", self._on_execution_requested)
            self.bus.subscribe("workflow_execution_requested", self._on_execution_requested)

    def stop(self) -> None:
        """Stop service."""
        logger.info("Stopping WorkflowExecutorIntegrationService...")
        self.cancel_current_execution("Service stopped")

    def is_healthy(self) -> bool:
        return True

    def cancel_current_execution(self, reason: str = "User cancelled") -> None:
        """Cancel active mission execution."""
        if self.coordinator:
            self.coordinator.cancel(reason)

    # ------------------------------------------------------------------
    # Event Handlers & Orchestration
    # ------------------------------------------------------------------

    def _on_execution_requested(self, payload: Any) -> None:
        """Handle execution request event asynchronously."""
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
        """
        Execute mission task graph.

        Args:
            mission_id: Mission ID.
            task_graph: TaskGraph containing tasks.

        Returns:
            MissionExecutionResult object.
        """
        logger.info(f"WorkflowExecutorIntegrationService executing mission '{mission_id}'...")
        result = await self.coordinator.execute_mission_plan(mission_id, task_graph)

        summary_text = self.result_formatter.format_summary(result)
        result.summary = summary_text

        # Publish response to Conversation Manager & TTS
        if self.bus:
            self.bus.publish("ai_response_ready", {"text": summary_text})
            self.bus.publish("workflow_completed", result.to_dict())

        return result
