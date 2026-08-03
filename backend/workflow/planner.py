import logging
import uuid
from typing import Any, Dict, List, Optional
from workflow.models import TaskType, WorkflowState
from workflow.task import WorkflowTask
from workflow.workflow import Workflow

logger = logging.getLogger("AURA.Workflow.Planner")


class WorkflowPlanner:
    """
    Decomposes natural language user goals into structured Workflow task graphs.
    """

    def plan_workflow(self, goal: str, context: Optional[Dict[str, Any]] = None) -> Workflow:
        """
        Create a structured Workflow DAG from a user goal string.

        Args:
            goal (str): Natural language mission statement.
            context (dict): Runtime context variables.

        Returns:
            Workflow: Structured workflow graph.
        """
        workflow_id = f"wf_{uuid.uuid4().hex[:8]}"
        workflow = Workflow(workflow_id=workflow_id, goal=goal, context=context or {})

        logger.info(f"Planning workflow for goal: '{goal}' (ID: {workflow_id})")

        # Rules-based goal decomposition templates
        goal_lower = goal.lower()

        if "react" in goal_lower or "portfolio" in goal_lower:
            t1 = WorkflowTask(task_id="create_project", tool="open_application", description="Create project directory", parameters={"app_name": "cmd.exe"}, task_type=TaskType.DESKTOP)
            t2 = WorkflowTask(task_id="install_deps", tool="type_text", description="Install dependencies", parameters={"text": "npm install"}, dependencies={"create_project"}, task_type=TaskType.TERMINAL)
            t3 = WorkflowTask(task_id="open_browser", tool="open_page", description="Launch browser", parameters={"url": "http://localhost:3000"}, dependencies={"install_deps"}, task_type=TaskType.BROWSER)
            workflow.add_task(t1)
            workflow.add_task(t2)
            workflow.add_task(t3)
        elif "downloads" in goal_lower or "organize" in goal_lower:
            t1 = WorkflowTask(task_id="scan_folder", tool="explorer_search", description="Scan Downloads folder", parameters={"directory": "C:\\Downloads", "query": "*"}, task_type=TaskType.FILE)
            t2 = WorkflowTask(task_id="create_dirs", tool="open_application", description="Create categorization folders", parameters={"app_name": "cmd.exe"}, dependencies={"scan_folder"}, task_type=TaskType.FILE)
            workflow.add_task(t1)
            workflow.add_task(t2)
        else:
            # Default single task fallback
            t1 = WorkflowTask(task_id="task_1", tool="chat", description=f"Execute mission: '{goal}'", parameters={"message": goal}, task_type=TaskType.REASONING)
            workflow.add_task(t1)

        workflow.state = WorkflowState.READY
        return workflow
