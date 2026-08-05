"""
Natural Language Task Decomposer.
Decomposes natural language user requests into structured sequence of PlannerTask nodes based on context.
"""

import logging
from typing import Any, Dict, List

from planner.models import PlanningContext, PlannerTask
from planner.task import TaskBuilder

logger = logging.getLogger("AURA.Planner.Decomposer")


class TaskDecomposer:
    """
    Decomposes requests into executable task steps.
    """

    def decompose(self, context: PlanningContext) -> List[PlannerTask]:
        """
        Decompose natural language request in context into sequence of PlannerTasks.

        Args:
            context: PlanningContext input state and request.

        Returns:
            List of PlannerTask objects.
        """
        req_lower = context.user_request.lower()
        tasks: List[PlannerTask] = []

        # Example: "Create a React project"
        if "react" in req_lower and "create" in req_lower:
            t1 = (
                TaskBuilder("Open Terminal", "launch_app")
                .with_inputs({"executable": "cmd.exe"})
                .with_outputs({"app_id": "term_1"})
                .with_verification({"app_name": "cmd.exe", "status": "running"})
                .mark_recovery_point(True)
                .build()
            )

            t2 = (
                TaskBuilder("Run npm create react app", "run_command")
                .with_inputs({"command": "npx create-react-app my-app"})
                .depends_on([t1.task_id])
                .with_verification({"command_exit_code": 0})
                .build()
            )

            t3 = (
                TaskBuilder("Wait for completion", "wait_condition")
                .with_inputs({"timeout_sec": 30.0})
                .depends_on([t2.task_id])
                .mark_recovery_point(True)
                .build()
            )

            t4 = (
                TaskBuilder("Verify project exists", "verify_goal")
                .with_inputs({"file_path": "my-app", "file_exists": True})
                .depends_on([t3.task_id])
                .with_verification({"file_exists": True})
                .build()
            )

            t5 = (
                TaskBuilder("Open VS Code", "launch_app")
                .with_inputs({"executable": "code.exe", "args": ["my-app"]})
                .depends_on([t4.task_id])
                .with_verification({"app_name": "code.exe", "status": "running"})
                .mark_recovery_point(True)
                .build()
            )

            tasks.extend([t1, t2, t3, t4, t5])

        else:
            # Default generic task decomposition
            t1 = (
                TaskBuilder(f"Process request: {context.user_request}", "execute_interaction")
                .with_inputs({"user_request": context.user_request})
                .with_verification({"status": "completed"})
                .mark_recovery_point(True)
                .build()
            )
            tasks.append(t1)

        logger.info(f"Decomposed request '{context.user_request}' into {len(tasks)} tasks")
        return tasks
