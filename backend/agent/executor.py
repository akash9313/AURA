import logging
import time
from typing import Optional
from agent.result import TaskResult
from agent.task import Task
from tools.registry import ToolRegistry
from tools.result import ToolResult as RegistryToolResult

logger = logging.getLogger("AURA.Agent.Executor")


class TaskExecutor:
    """
    Executes individual Agent Tasks using the ToolRegistry abstraction.
    """

    def __init__(self, registry: ToolRegistry = None):
        self.registry = registry if registry is not None else ToolRegistry(auto_discover=True)

    def execute_task(self, task: Task) -> TaskResult:
        """
        Resolve tool, validate parameters, and execute task.

        Args:
            task (Task): Task instance to execute.

        Returns:
            TaskResult: Standardized execution result.
        """
        start_time = time.time()
        tool_name = task.tool_name
        parameters = task.parameters

        logger.info(f"⚡ TaskExecutor executing task '{task.task_id}' using tool '{tool_name}'")

        # 1. Resolve Tool
        tool = self.registry.get(tool_name)
        if not tool:
            elapsed = time.time() - start_time
            err = f"Tool '{tool_name}' not found in registry."
            logger.error(err)
            return TaskResult(
                success=False,
                error=err,
                execution_time=elapsed
            )

        # 2. Execute Tool
        try:
            res = tool.execute(parameters)
            elapsed = time.time() - start_time

            if isinstance(res, RegistryToolResult):
                return TaskResult(
                    success=res.success,
                    output=res.message,
                    error=res.message if not res.success else None,
                    logs=[f"Executed {tool_name} in {res.execution_time:.3f}s"],
                    execution_time=elapsed,
                    metadata=res.to_dict()
                )
            elif isinstance(res, dict):
                return TaskResult(
                    success=res.get("success", True),
                    output=res.get("message") or res.get("output"),
                    error=res.get("message") if not res.get("success", True) else None,
                    execution_time=elapsed,
                    metadata=res
                )

            return TaskResult(
                success=True,
                output=str(res),
                execution_time=elapsed
            )
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"Task '{task.task_id}' execution error: {e}")
            return TaskResult(
                success=False,
                error=str(e),
                execution_time=elapsed
            )