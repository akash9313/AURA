import logging
from typing import Dict, List, Tuple
from agent.task import Task
from tools.registry import ToolRegistry

logger = logging.getLogger("AURA.Agent.Validator")


class TaskValidator:
    """
    Validates task eligibility, parameter schemas, dependency completion, and execution safety.
    """

    def __init__(self, registry: ToolRegistry = None):
        self.registry = registry if registry is not None else ToolRegistry(auto_discover=True)

    def validate_task(self, task: Task, completed_task_ids: List[str]) -> Tuple[bool, str]:
        """
        Validate if a task is ready and safe to execute.

        Returns:
            Tuple[bool, str]: (is_valid, validation_message)
        """
        # 1. Tool Existence Check
        tool = self.registry.get(task.tool_name)
        if not tool:
            msg = f"Tool '{task.tool_name}' is not registered in ToolRegistry."
            logger.warning(msg)
            return False, msg

        # 2. Dependency Completion Check
        if not task.is_ready(completed_task_ids):
            missing_deps = [d for d in task.dependencies if d not in completed_task_ids]
            msg = f"Task '{task.task_id}' is waiting on incomplete dependencies: {missing_deps}"
            logger.warning(msg)
            return False, msg

        # 3. Parameters Validation
        if not isinstance(task.parameters, dict):
            msg = f"Task parameters must be a dictionary, got {type(task.parameters).__name__}"
            logger.warning(msg)
            return False, msg

        return True, "Task validation passed."
