"""
Recovery Point Manager.
Identifies and tags checkpoint tasks within a MissionPlan task graph for error recovery.
"""

import logging
from typing import List

from planner.models import MissionPlan, TaskGraph

logger = logging.getLogger("AURA.Planner.RecoveryPoints")


class RecoveryPointManager:
    """
    Manages recovery checkpoint identification in task graphs.
    """

    def identify_recovery_points(self, graph: TaskGraph) -> List[str]:
        """
        Identify task IDs that serve as recovery points.

        Returns:
            List of recovery point task_ids.
        """
        rec_ids = []
        for tid, task in graph.tasks.items():
            if task.is_recovery_point or not task.dependencies:
                rec_ids.append(tid)

        logger.debug(f"Identified {len(rec_ids)} recovery points in TaskGraph '{graph.graph_id}'")
        return rec_ids
