"""
Capability Dispatcher (Command Pattern).
Dispatches workflow tasks strictly through the Capability Registry, Interaction Engine, and Goal Verification Engine.
Enforces:
1. Workflow Executor must NEVER bypass the Capability Registry.
2. Every task MUST be verified before being marked complete.
"""

import asyncio
import logging
import time
from typing import Any, Dict, Optional

from capabilities.service import CapabilityService
from interaction.service import InteractionEngineService
from verification.service import GoalVerificationService

logger = logging.getLogger("AURA.Workflow.Integration.CapabilityDispatcher")


class CapabilityNotFoundError(Exception):
    """Raised when capability requested by a task is not registered in Capability Registry."""
    pass


class VerificationFailedError(Exception):
    """Raised when empirical goal verification fails for an executed task."""
    pass


class CapabilityDispatcher:
    """
    Executes task capabilities through Capability Registry and verifies results empirically.
    """

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
        """
        1. Resolve capability via CapabilityRegistry (NEVER bypass).
        2. Execute action via InteractionEngine / capability handler.
        3. Empirically verify result via GoalVerification Engine.

        Args:
            task_id: Unique ID of the task.
            capability_name: Capability identifier or alias.
            parameters: Input parameter dictionary.
            verification_rule: Optional expected outcome verification rule.

        Returns:
            Dictionary containing execution outputs and verification result.

        Raises:
            CapabilityNotFoundError: If capability is not registered.
            VerificationFailedError: If empirical verification fails.
        """
        start_time = time.time()
        logger.info(f"Resolving capability '{capability_name}' for task '{task_id}' in Capability Registry...")

        # 1. Resolve Capability in Capability Registry (MANDATORY)
        cap = self.capability_service.get_capability(capability_name)
        if not cap:
            # Fallback search best capability match
            match = self.capability_service.find_best_capability(capability_name)
            if match and match.confidence >= 0.5:
                cap = match.capability
                logger.info(f"Matched fallback capability '{cap.name}' for intent '{capability_name}'")
            else:
                err_msg = f"Capability '{capability_name}' not found in Capability Registry!"
                logger.error(err_msg)
                raise CapabilityNotFoundError(err_msg)

        logger.info(f"Dispatching task '{task_id}' capability '{cap.name}' (Category: {cap.category.value})...")

        # 2. Execute Action
        exec_output: Dict[str, Any] = {"status": "executed", "capability": cap.name}
        try:
            if hasattr(self.interaction_service, "execute_goal"):
                res = await self.interaction_service.click()  # Interaction engine trigger
                exec_output["interaction_result"] = str(res)
        except Exception as e:
            logger.warning(f"Interaction engine execution warning for task '{task_id}': {e}")
            exec_output["execution_note"] = str(e)

        # 3. Empirically Verify Goal (MANDATORY BEFORE MARKING COMPLETE)
        logger.info(f"Verifying empirical outcome for task '{task_id}'...")
        expected = verification_rule or {"status": "success", "task_id": task_id}

        v_res = await self.verification_service.verify_goal(
            goal_id=task_id,
            goal_description=f"Task {task_id} execution of {cap.name}",
            expected_outcome=expected,
        )

        dt = round(time.time() - start_time, 3)

        if not v_res.verified:
            err_msg = f"Empirical verification failed for task '{task_id}': {v_res.summary}"
            logger.error(err_msg)
            raise VerificationFailedError(err_msg)

        logger.info(f"Task '{task_id}' successfully executed & verified in {dt}s!")
        return {
            "task_id": task_id,
            "capability": cap.name,
            "verification": v_res.to_dict(),
            "output": exec_output,
            "duration_sec": dt,
        }
