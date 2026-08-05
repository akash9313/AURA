import logging
from typing import Optional

from planner.integration.configuration import PlannerIntegrationConfig
from planner.integration.models import Mission, MissionStatus

logger = logging.getLogger("AURA.Planner.Integration.ResponseFormatter")


class ResponseFormatter:
    def __init__(self, config: Optional[PlannerIntegrationConfig] = None):
        self.config = config or PlannerIntegrationConfig()

    def format_response(self, mission: Mission) -> str:
        if mission.status == MissionStatus.COMPLETED:
            if "output" in mission.result_data:
                return str(mission.result_data["output"])
            return f"I have completed your request: '{mission.goal}'."

        elif mission.status == MissionStatus.FAILED:
            err = mission.error_message or "An unexpected error occurred during execution."
            return f"I ran into an issue while processing your request: {err}"

        elif mission.status == MissionStatus.PLANNED:
            return f"Mission planned for: '{mission.goal}'. Beginning execution."

        return self.config.fallback_response
