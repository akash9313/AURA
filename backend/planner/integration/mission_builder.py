"""
Mission Builder.
Assembles complete Mission domain models from MissionRequests and Planner MissionPlans.
"""

import logging
from typing import Any, List, Optional

from planner.integration.models import (
    Mission,
    MissionExecutionMode,
    MissionPriority,
    MissionRequest,
    MissionStatus,
)
from planner.models import MissionPlan

logger = logging.getLogger("AURA.Planner.Integration.MissionBuilder")


class MissionBuilder:
    """
    Constructs validated Mission instances from request metadata and AI Planner outputs.
    """

    def build_mission(
        self,
        request: MissionRequest,
        plan: Optional[MissionPlan] = None,
        confidence: float = 1.0,
        error_message: Optional[str] = None,
    ) -> Mission:
        """
        Build Mission object.

        Args:
            request: The parsed MissionRequest.
            plan: The optional generated MissionPlan from AIPlanner.
            confidence: Planner confidence score (0.0 to 1.0).
            error_message: Error string if planning failed.

        Returns:
            Mission domain object.
        """
        required_caps: List[str] = []
        goal_summary = request.original_user_request
        expected_outcome = f"Execute steps for: {request.original_user_request}"

        if plan:
            goal_summary = plan.goal_summary or goal_summary
            expected_outcome = f"Successfully completed mission: {goal_summary}"
            # Extract capabilities required from task graph
            if hasattr(plan, "task_graph") and hasattr(plan.task_graph, "tasks"):
                for task in plan.task_graph.tasks.values():
                    cap = getattr(task, "capability_required", "")
                    if cap and cap not in required_caps:
                        required_caps.append(cap)

        status = MissionStatus.PLANNED if plan else (MissionStatus.FAILED if error_message else MissionStatus.CREATED)

        mission = Mission(
            original_user_request=request.original_user_request,
            goal=goal_summary,
            priority=request.priority,
            required_capabilities=required_caps,
            expected_outcome=expected_outcome,
            planner_confidence=confidence,
            execution_mode=MissionExecutionMode.AUTOMATIC,
            status=status,
            plan=plan,
            error_message=error_message,
        )

        logger.info(f"Built Mission '{mission.mission_id}' with status '{mission.status.value}' and {len(required_caps)} capabilities required.")
        return mission
