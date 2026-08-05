"""
Response Formatter.
Formats Mission execution outputs and errors into natural language responses for Conversation Manager & TTS.
"""

import logging
from typing import Optional

from planner.integration.configuration import PlannerIntegrationConfig
from planner.integration.models import Mission, MissionStatus

logger = logging.getLogger("AURA.Planner.Integration.ResponseFormatter")


class ResponseFormatter:
    """
    Formats Mission state and outcomes into spoken/displayable text.
    """

    def __init__(self, config: Optional[PlannerIntegrationConfig] = None):
        self.config = config or PlannerIntegrationConfig()

    def format_response(self, mission: Mission) -> str:
        """
        Format Mission into natural language string for Conversation Manager.

        Args:
            mission: The Mission object to format.

        Returns:
            Displayable/spoken response string.
        """
        if mission.status == MissionStatus.COMPLETED:
            if "output" in mission.result_data:
                return str(mission.result_data["output"])
            return f"I have completed your request: '{mission.goal}'."

        elif mission.status == MissionStatus.FAILED:
            err = mission.error_message or "An unexpected error occurred during execution."
            logger.warning(f"Formatting failed mission response: {err}")
            return f"I ran into an issue while processing your request: {err}"

        elif mission.status == MissionStatus.PLANNED:
            return f"Mission planned for: '{mission.goal}'. Beginning execution."

        return self.config.fallback_response
