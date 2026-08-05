import logging
import time
from typing import Any, Dict, List, Optional

from planner.configuration import PlannerConfig
from planner.decomposer import TaskDecomposer
from planner.events import PlannerEvent
from planner.graph import TaskGraphBuilder
from planner.models import (
    MissionPlan,
    PlanningContext,
    PlanningResult,
)
from planner.recovery_points import RecoveryPointManager
from planner.validator import PlanValidator

logger = logging.getLogger("AURA.Planner.Engine")


class AIPlanner:
    def __init__(
        self,
        bus: Any = None,
        config: Optional[PlannerConfig] = None,
    ):
        self.bus = bus
        self.config = config or PlannerConfig()

        self.decomposer = TaskDecomposer()
        self.graph_builder = TaskGraphBuilder()
        self.validator = PlanValidator()
        self.recovery_manager = RecoveryPointManager()

    async def create_plan(self, context: PlanningContext) -> PlanningResult:
        start_time = time.time()
        self._publish_event(PlannerEvent.MISSION_STARTED, {"user_request": context.user_request})

        try:
            tasks = self.decomposer.decompose(context)
            task_graph = self.graph_builder.build_graph(tasks)
            rec_points = self.recovery_manager.identify_recovery_points(task_graph)

            plan = MissionPlan(
                user_request=context.user_request,
                goal_summary=f"Mission Plan for: {context.user_request}",
                task_graph=task_graph,
                recovery_points=rec_points,
            )

            is_valid, errors = self.validator.validate_plan(plan)
            if not is_valid:
                msg = f"Plan validation failed: {errors}"
                self._publish_event(PlannerEvent.PLAN_FAILED, {"error": msg})
                return PlanningResult(success=False, plan=None, message=msg)

            duration_ms = round((time.time() - start_time) * 1000, 2)
            self._publish_event(PlannerEvent.PLAN_CREATED, plan.to_dict())

            return PlanningResult(
                success=True,
                plan=plan,
                message="Plan created successfully",
                duration_ms=duration_ms,
            )

        except Exception as e:
            msg = f"Planning failed: {str(e)}"
            self._publish_event(PlannerEvent.PLAN_FAILED, {"error": msg})
            return PlanningResult(success=False, plan=None, message=msg)

    def _publish_event(self, event: PlannerEvent, data: Dict[str, Any]) -> None:
        if self.bus:
            try:
                self.bus.publish(event.value, data)
            except Exception as e:
                logger.error(f"Failed to publish planner event '{event.value}': {e}")
