"""
Unified Interaction Engine Service.
Top-level AURA service integrating the Interaction Engine into the kernel framework.
Abstracts interaction strategy decisions from the Workflow Engine.
"""

import logging
from typing import Any, Dict, Optional

from core.service import Service
from interaction.configuration import InteractionEngineConfig
from interaction.executor import InteractionExecutor
from interaction.models import (
    InteractionGoal,
    InteractionIntent,
    InteractionMethod,
    InteractionResult,
    InteractionTarget,
)

logger = logging.getLogger("AURA.Interaction.Service")


class InteractionEngineService(Service):
    """
    Service wrapper exposing high-level goal interaction capabilities to AURA Runtime and Workflow Engine.
    """

    def __init__(
        self,
        bus: Any = None,
        config: Optional[InteractionEngineConfig] = None,
    ):
        super().__init__(bus)
        self.config = config or InteractionEngineConfig()
        self.executor = InteractionExecutor(bus=bus, config=self.config)
        logger.info("InteractionEngineService initialized")

    async def execute_goal(
        self,
        intent: InteractionIntent,
        target: Optional[InteractionTarget] = None,
        params: Optional[Dict[str, Any]] = None,
        preferred_method: Optional[InteractionMethod] = None,
    ) -> InteractionResult:
        """
        Execute high-level interaction goal.

        Returns:
            InteractionResult payload.
        """
        goal = InteractionGoal(
            intent=intent,
            target=target or InteractionTarget(),
            params=params or {},
            preferred_method=preferred_method,
        )
        return await self.executor.execute_goal(goal)

    async def click(self, target: Optional[InteractionTarget] = None) -> InteractionResult:
        """Click target element."""
        return await self.execute_goal(InteractionIntent.CLICK, target=target)

    async def type_text(self, text: str, target: Optional[InteractionTarget] = None) -> InteractionResult:
        """Type text into target control."""
        tgt = target or InteractionTarget()
        tgt.text_value = text
        return await self.execute_goal(InteractionIntent.TYPE, target=tgt, params={"text": text})

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        logger.info("Starting InteractionEngineService...")

    def stop(self) -> None:
        logger.info("Stopping InteractionEngineService...")

    def is_healthy(self) -> bool:
        return True
