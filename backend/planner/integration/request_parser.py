"""
Request Parser.
Parses natural language user transcripts into validated MissionRequest instances.
"""

import logging
from typing import Any, Dict, Optional

from planner.integration.models import MissionPriority, MissionRequest

logger = logging.getLogger("AURA.Planner.Integration.RequestParser")


class RequestParser:
    """
    Parses and sanitizes natural language user input into MissionRequest objects.
    """

    def parse_request(
        self,
        raw_transcript: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> MissionRequest:
        """
        Parse raw transcript string and assemble MissionRequest.

        Args:
            raw_transcript: User speech/text input string.
            context: Optional environment/session context.

        Returns:
            MissionRequest object.

        Raises:
            ValueError: If transcript is empty or whitespace-only.
        """
        if not raw_transcript or not raw_transcript.strip():
            raise ValueError("Transcript is empty or blank")

        sanitized_text = raw_transcript.strip()
        priority = self._determine_priority(sanitized_text)

        logger.info(f"Parsed request: '{sanitized_text}' with priority '{priority.value}'")

        return MissionRequest(
            original_user_request=sanitized_text,
            context=context or {},
            priority=priority,
        )

    def _determine_priority(self, text: str) -> MissionPriority:
        lower = text.lower()
        if "critical" in lower or "emergency" in lower:
            return MissionPriority.CRITICAL
        elif "urgent" in lower or "asap" in lower or "immediately" in lower:
            return MissionPriority.HIGH
        elif "low priority" in lower or "whenever" in lower:
            return MissionPriority.LOW
        return MissionPriority.NORMAL
