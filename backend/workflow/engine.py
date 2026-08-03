import logging
from typing import Any, Dict, Optional

from tools.registry import ToolRegistry
from workflow.executor import WorkflowExecutor
from workflow.history import WorkflowHistoryManager
from workflow.models import WorkflowState
from workflow.observer import WorkflowObserver
from workflow.planner import WorkflowPlanner
from workflow.reporter import WorkflowReporter
from workflow.scheduler import WorkflowScheduler
from workflow.validator import WorkflowValidator
from workflow.workflow import Workflow

logger = logging.getLogger("AURA.Workflow.Engine")


class WorkflowEngine:
    """
    Master Autonomous Workflow Engine Orchestrator.
    Manages complete mission lifecycles: Planning -> Validation -> Scheduling -> Execution -> Recovery -> Reporting -> Archive.
    """

    def __init__(self, bus=None, tool_registry: Optional[ToolRegistry] = None):
        self.bus = bus
        self.tool_registry = tool_registry if tool_registry is not None else ToolRegistry()
        self.planner = WorkflowPlanner()
        self.validator = WorkflowValidator()
        self.scheduler = WorkflowScheduler()
        self.observer = WorkflowObserver(bus=self.bus)
        self.executor = WorkflowExecutor(tool_registry=self.tool_registry, observer=self.observer)
        self.reporter = WorkflowReporter()
        self.history = WorkflowHistoryManager()

    def run_mission(self, goal: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute an autonomous multi-step mission end-to-end.

        Args:
            goal (str): Natural language user goal.
            context (dict): Runtime variables.

        Returns:
            Dict[str, Any]: Comprehensive execution report.
        """
        logger.info(f"🚀 Launching Autonomous Mission Goal: '{goal}'")

        # 1. Plan
        workflow = self.planner.plan_workflow(goal, context)

        # 2. Validate
        workflow.state = WorkflowState.VALIDATING
        self.validator.validate(workflow)

        # 3. Schedule
        self.scheduler.schedule_immediate(workflow)
        scheduled_wf = self.scheduler.get_next()

        if not scheduled_wf:
            raise RuntimeError("Failed to retrieve scheduled workflow.")

        # 4. Execute
        finished_wf = self.executor.execute_workflow(scheduled_wf)

        # 5. Archive & Report
        self.history.archive(finished_wf)
        report = self.reporter.generate_report(finished_wf)
        return report
