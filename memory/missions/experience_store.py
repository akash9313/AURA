import logging
from typing import Dict, List, Optional

from memory.missions.models import MissionExperience

logger = logging.getLogger("AURA.Memory.Missions.ExperienceStore")


class ExperienceStore:
    def __init__(self):
        self._experiences: Dict[str, MissionExperience] = {}

    def save(self, exp: MissionExperience) -> None:
        self._experiences[exp.experience_id] = exp

    def get(self, experience_id: str) -> Optional[MissionExperience]:
        return self._experiences.get(experience_id)

    def list_all(self) -> List[MissionExperience]:
        return list(self._experiences.values())
