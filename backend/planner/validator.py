"""
Plan & Task Graph Validator.
Validates mission plans and task graph DAGs for structural integrity, unknown capabilities, and missing dependencies.
"""

import logging
from typing import List, Tuple

from planner.models import MissionPlan, TaskGraph

logger = logging.getLogger("AURA.Planner.Validator")


class PlanValidator:
    """
    Validates MissionPlan and TaskGraph for execution readiness.
    """

    def validate_plan(self, plan: MissionPlan) -> Tuple[bool, List[str]]:
        """
        Validate MissionPlan.

        Returns:
            Tuple of (is_valid: bool, List of error messages)
        """
        errors = []
        graph = plan.task_graph

        if not graph.tasks:
            errors.append("Mission plan contains no tasks")
            return (False, errors)

        for tid, task in graph.tasks.items():
            if not task.capability_required:
                errors.append(f"Task '{tid}' missing required capability")

            for dep_id in task.dependencies:
                if dep_id not in graph.tasks:
                    errors.append(f"Task '{tid}' references missing dependency '{dep_id}'")

        is_valid = len(errors) == 0
        if is_valid:
            logger.info(f"MissionPlan '{plan.plan_id}' passed validation successfully")
        else:
            logger.warning(f"MissionPlan '{plan.plan_id}' failed validation: {errors}")

        return (is_valid, errors)
