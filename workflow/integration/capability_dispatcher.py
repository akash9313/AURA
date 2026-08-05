import asyncio
import logging
import time
from typing import Any, Dict, Optional

from capabilities.service import CapabilityService
from interaction.service import InteractionEngineService
from verification.service import GoalVerificationService

logger = logging.getLogger("AURA.Workflow.Integration.CapabilityDispatcher")


class CapabilityNotFoundError(Exception):
    pass


class VerificationFailedError(Exception):
    pass


class CapabilityDispatcher:
    def __init__(
        self,
        capability_service: Optional[CapabilityService] = None,
        interaction_service: Optional[InteractionEngineService] = None,
        verification_service: Optional[GoalVerificationService] = None,
    ):
        self.capability_service = capability_service or CapabilityService()
        self.interaction_service = interaction_service or InteractionEngineService()
        self.verification_service = verification_service or GoalVerificationService()

    async def dispatch_and_verify_task(
        self,
        task_id: str,
        capability_name: str,
        parameters: Dict[str, Any],
        verification_rule: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        start_time = time.time()
        cap = self.capability_service.get_capability(capability_name)
        if not cap:
            match = self.capability_service.find_best_capability(capability_name)
            if match and match.confidence >= 0.5:
                cap = match.capability
            else:
                err_msg = f"Capability '{capability_name}' not found in Capability Registry!"
                raise CapabilityNotFoundError(err_msg)

        exec_output: Dict[str, Any] = {"status": "executed", "capability": cap.name}
        try:
            if hasattr(self.interaction_service, "execute_goal"):
                res = await self.interaction_service.click()
                exec_output["interaction_result"] = str(res)
        except Exception as e:
            exec_output["execution_note"] = str(e)

        expected = verification_rule or {"status": "success", "task_id": task_id}
        v_res = await self.verification_service.verify_goal(
            goal_id=task_id,
            goal_description=f"Task {task_id} execution of {cap.name}",
            expected_outcome=expected,
        )

        dt = round(time.time() - start_time, 3)

        if not v_res.verified:
            err_msg = f"Empirical verification failed for task '{task_id}': {v_res.summary}"
            raise VerificationFailedError(err_msg)

        return {
            "task_id": task_id,
            "capability": cap.name,
            "verification": v_res.to_dict(),
            "output": exec_output,
            "duration_sec": dt,
        }
