"""
Mission Experience Storage Store.
Persists distilled MissionExperience objects for AI Planner knowledge retrieval.
"""

import logging
from typing import Dict, List, Optional

from memory.missions.models import MissionExperience

logger = logging.getLogger("AURA.Memory.Missions.ExperienceStore")


class ExperienceStore:
    """
    In-memory repository storing MissionExperience instances.
    """

    def __init__(self):
        self._experiences: Dict[str, MissionExperience] = {}

    def save(self, exp: MissionExperience) -> None:
        """Save experience object."""
        self._experiences[exp.experience_id] = exp
        logger.debug(f"Saved MissionExperience '{exp.experience_id}'")

    def get(self, experience_id: str) -> Optional[MissionExperience]:
        """Get experience by ID."""
        return self._experiences.get(experience_id)

    def list_all(self) -> List[MissionExperience]:
        """List all stored experiences."""
        return list(self._experiences.values())
