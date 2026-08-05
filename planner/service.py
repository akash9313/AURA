import logging
from typing import Any, Dict, List, Optional

from core.service import Service
from planner.configuration import PlannerConfig
from planner.models import MissionPlan, PlanningContext, PlanningResult
from planner.planner import AIPlanner

logger = logging.getLogger("AURA.Planner.Service")


class AIPlannerService(Service):
    def __init__(
        self,
        bus: Any = None,
        config: Optional[PlannerConfig] = None,
    ):
        super().__init__(bus)
        self.config = config or PlannerConfig()
        self.planner = AIPlanner(bus=bus, config=self.config)

    async def create_plan(
        self,
        user_request: str,
        current_memory: Optional[Dict[str, Any]] = None,
        available_tools: Optional[List[str]] = None,
        desktop_state: Optional[Dict[str, Any]] = None,
        browser_state: Optional[Dict[str, Any]] = None,
        application_state: Optional[Dict[str, Any]] = None,
    ) -> PlanningResult:
        ctx = PlanningContext(
            user_request=user_request,
            current_memory=current_memory or {},
            available_tools=available_tools or [],
            desktop_state=desktop_state or {},
            browser_state=browser_state or {},
            application_state=application_state or {},
        )
        return await self.planner.create_plan(ctx)

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def is_healthy(self) -> bool:
        return True
