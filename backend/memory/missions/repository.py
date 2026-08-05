"""
Mission Composite Repository Pattern.
Combines MissionStore, ExperienceStore, CheckpointStore, and MissionSearchEngine under a unified repository interface.
"""

import logging
from typing import List, Optional

from memory.missions.checkpoint_store import CheckpointStore
from memory.missions.experience_store import ExperienceStore
from memory.missions.mission_store import MissionStore
from memory.missions.models import (
    MissionCheckpointRecord,
    MissionExperience,
    MissionRecord,
)
from memory.missions.search import MissionSearchEngine

logger = logging.getLogger("AURA.Memory.Missions.Repository")


class MissionRepository:
    """
    Unified composite repository for all operational mission data.
    """

    def __init__(self):
        self.mission_store = MissionStore()
        self.experience_store = ExperienceStore()
        self.checkpoint_store = CheckpointStore()
        self.search_engine = MissionSearchEngine(self.experience_store)

    def save_mission(self, record: MissionRecord) -> None:
        self.mission_store.save(record)

    def get_mission(self, mission_id: str) -> Optional[MissionRecord]:
        return self.mission_store.get(mission_id)

    def save_experience(self, exp: MissionExperience) -> None:
        self.experience_store.save(exp)

    def get_experience(self, experience_id: str) -> Optional[MissionExperience]:
        return self.experience_store.get(experience_id)

    def search_experiences_by_goal(self, goal_query: str, top_k: int = 5) -> List[MissionExperience]:
        return self.search_engine.search_by_goal(goal_query, top_k)
