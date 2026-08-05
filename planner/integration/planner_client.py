import asyncio
import logging
import time
from typing import Any, Dict, Optional

from planner.configuration import PlannerConfig
from planner.integration.configuration import PlannerIntegrationConfig
from planner.integration.models import Mission, MissionRequest, MissionStatus
from planner.models import PlanningContext, PlanningResult
from planner.planner import AIPlanner
from workflow.executor.workflow_executor import WorkflowExecutor
from workflow.graph.graph import TaskGraphEngine

logger = logging.getLogger("AURA.Planner.Integration.PlannerClient")


class PlannerClient:
    def __init__(
        self,
        planner: Optional[AIPlanner] = None,
        workflow_executor: Optional[WorkflowExecutor] = None,
        config: Optional[PlannerIntegrationConfig] = None,
    ):
        self.planner = planner or AIPlanner()
        self.workflow_executor = workflow_executor
        self.config = config or PlannerIntegrationConfig()

    async def generate_plan(self, request: MissionRequest) -> PlanningResult:
        context = PlanningContext(
            user_request=request.original_user_request,
            current_memory=request.context,
        )

        last_error = ""
        for attempt in range(1, self.config.max_retries + 1):
            try:
                result = await asyncio.wait_for(
                    self.planner.create_plan(context),
                    timeout=self.config.planner_timeout_sec,
                )

                if result.success:
                    return result

                last_error = result.message
            except asyncio.TimeoutError:
                last_error = f"Planner timed out after {self.config.planner_timeout_sec} seconds"
            except Exception as e:
                last_error = f"Planner execution exception: {str(e)}"

            if attempt < self.config.max_retries:
                await asyncio.sleep(self.config.backoff_sec)

        return PlanningResult(
            success=False,
            plan=None,
            message=f"Failed to generate plan after {self.config.max_retries} attempts. Last error: {last_error}",
        )

    async def execute_mission(self, mission: Mission) -> Dict[str, Any]:
        if not mission.plan or not hasattr(mission.plan, "task_graph"):
            raise ValueError("Mission has no valid task graph plan to execute")

        executor = self.workflow_executor or WorkflowExecutor()

        graph_engine = TaskGraphEngine()
        if hasattr(mission.plan.task_graph, "tasks"):
            for tid, ptask in mission.plan.task_graph.tasks.items():
                graph_engine.add_task(
                    task_id=tid,
                    name=getattr(ptask, "description", tid),
                    tool=getattr(ptask, "capability_required", "generic_capability"),
                    parameters=getattr(ptask, "inputs", {}),
                    dependencies=getattr(ptask, "dependencies", []),
                )

        exec_result = await executor.execute_graph(graph_engine)

        return {
            "success": exec_result.success,
            "workflow_id": exec_result.workflow_id,
            "tasks_executed": exec_result.completed_tasks,
            "error": exec_result.message if not exec_result.success else None,
            "output": f"Executed mission successfully with {len(exec_result.completed_tasks)} tasks completed.",
        }
