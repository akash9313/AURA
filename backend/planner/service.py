"""
AI Planner Service.
Top-level AURA service integrating the AI Planner Engine into the kernel framework.
Converts user natural language requests into executable task graphs without executing actions.
"""

import logging
from typing import Any, Dict, List, Optional

from core.service import Service
from planner.configuration import PlannerConfig
from planner.models import MissionPlan, PlanningContext, PlanningResult
from planner.planner import AIPlanner

logger = logging.getLogger("AURA.Planner.Service")


class AIPlannerService(Service):
    """
    Service wrapper exposing AI Planner capabilities to AURA Runtime and Workflow Engine.
    """

    def __init__(
        self,
        bus: Any = None,
        config: Optional[PlannerConfig] = None,
    ):
        super().__init__(bus)
        self.config = config or PlannerConfig()
        self.planner = AIPlanner(bus=bus, config=self.config)
        logger.info("AIPlannerService initialized")

    async def create_plan(
        self,
        user_request: str,
        current_memory: Optional[Dict[str, Any]] = None,
        available_tools: Optional[List[str]] = None,
        desktop_state: Optional[Dict[str, Any]] = None,
        browser_state: Optional[Dict[str, Any]] = None,
        application_state: Optional[Dict[str, Any]] = None,
    ) -> PlanningResult:
        """
        Create a validated MissionPlan for a natural language request.

        Returns:
            PlanningResult object.
        """
        ctx = PlanningContext(
            user_request=user_request,
            current_memory=current_memory or {},
            available_tools=available_tools or [],
            desktop_state=desktop_state or {},
            browser_state=browser_state or {},
            application_state=application_state or {},
        )
        return await self.planner.create_plan(ctx)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        logger.info("Starting AIPlannerService...")

    def stop(self) -> None:
        logger.info("Stopping AIPlannerService...")

    def is_healthy(self) -> bool:
        return True
