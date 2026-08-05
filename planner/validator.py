import logging
from typing import List, Tuple

from planner.models import MissionPlan, TaskGraph

logger = logging.getLogger("AURA.Planner.Validator")


class PlanValidator:
    def validate_plan(self, plan: MissionPlan) -> Tuple[bool, List[str]]:
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
        return (is_valid, errors)
