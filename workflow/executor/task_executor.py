import logging
import time
from typing import Any, Dict, Optional, Tuple

from capabilities.service import CapabilityService
from interaction.models import InteractionTarget
from interaction.service import InteractionEngineService
from verification.service import GoalVerificationService
from workflow.executor.models import WorkflowTaskExecution, WorkflowTaskState

logger = logging.getLogger("AURA.Workflow.Executor.TaskExecutor")


class TaskExecutor:
    def __init__(
        self,
        capability_service: Optional[CapabilityService] = None,
        interaction_service: Optional[InteractionEngineService] = None,
        verification_service: Optional[GoalVerificationService] = None,
    ):
        self.capability_service = capability_service
        self.interaction_service = interaction_service
        self.verification_service = verification_service

    async def execute_task(self, task_exec: WorkflowTaskExecution) -> Tuple[bool, str, Dict[str, Any]]:
        start_time = time.time()

        if self.capability_service:
            cap = self.capability_service.get_capability(task_exec.capability)
            if not cap:
                msg = f"Required capability '{task_exec.capability}' not registered in Capability Registry"
                return (False, msg, {})

        outputs = {"status": "executed", "timestamp": time.time()}
        if self.interaction_service:
            tgt = InteractionTarget(name=task_exec.name, text_value=task_exec.inputs.get("text"))
            res = await self.interaction_service.click(target=tgt)
            outputs.update(res.data or {})

        if self.verification_service and task_exec.inputs.get("verification_rule"):
            v_res = await self.verification_service.verify_goal(
                goal_id=task_exec.task_id,
                criteria={"rule": task_exec.inputs.get("verification_rule")},
            )
            if not v_res.verified:
                msg = f"Task verification failed: {v_res.summary}"
                return (False, msg, outputs)

        duration_ms = round((time.time() - start_time) * 1000, 2)
        task_exec.duration_ms = duration_ms
        msg = f"Task '{task_exec.task_id}' executed successfully in {duration_ms}ms"
        return (True, msg, outputs)
