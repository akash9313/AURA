import logging
from typing import List

from planner.models import MissionPlan, TaskGraph

logger = logging.getLogger("AURA.Planner.RecoveryPoints")


class RecoveryPointManager:
    def identify_recovery_points(self, graph: TaskGraph) -> List[str]:
        rec_ids = []
        for tid, task in graph.tasks.items():
            if task.is_recovery_point or not task.dependencies:
                rec_ids.append(tid)
        return rec_ids
