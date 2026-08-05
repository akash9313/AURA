"""
Mission Memory Engine Service.
Top-level AURA service integrating Mission Memory into the kernel framework.
Stores operational workflow knowledge and exposes semantic experience search to the AI Planner.
Coexists with Conversation Memory.
"""

import logging
from typing import Any, Dict, List, Optional

from core.service import Service
from memory.missions.configuration import MissionMemoryConfig
from memory.missions.events import MissionMemoryEvent
from memory.missions.models import MissionExperience, MissionRecord
from memory.missions.repository import MissionRepository
from memory.missions.retention import MissionRetentionPolicy
from memory.missions.summarizer import MissionSummarizer

logger = logging.getLogger("AURA.Memory.Missions.Service")


class MissionMemoryService(Service):
    """
    Service wrapper exposing Mission Memory Engine capabilities to AURA Runtime and AI Planner.
    """

    def __init__(
        self,
        bus: Any = None,
        config: Optional[MissionMemoryConfig] = None,
    ):
        super().__init__(bus)
        self.config = config or MissionMemoryConfig()
        self.repository = MissionRepository()
        self.summarizer = MissionSummarizer()
        self.retention_policy = MissionRetentionPolicy(self.config)
        logger.info("MissionMemoryService initialized")

    def record_mission_execution(
        self,
        goal: str,
        capabilities_used: List[str],
        duration_ms: float = 0.0,
        status: str = "completed",
        failures: List[str] = None,
        recoveries: List[str] = None,
        inputs: Dict[str, Any] = None,
        outputs: Dict[str, Any] = None,
    ) -> MissionRecord:
        """
        Record full operational mission execution and distill MissionExperience.

        Returns:
            Recorded MissionRecord instance.
        """
        record = MissionRecord(
            goal=goal,
            mission_type="desktop_workflow",
            status=status,
            duration_ms=duration_ms,
            inputs=inputs or {},
            outputs=outputs or {},
            capabilities_used=capabilities_used or [],
            failures=failures or [],
            recoveries=recoveries or [],
        )

        summary, lessons = self.summarizer.summarize_mission(record)
        record.reflection_summary = summary
        self.repository.save_mission(record)
        self._publish_event(MissionMemoryEvent.MISSION_STORED, record.to_dict())

        # Distill MissionExperience for Planner
        exp = MissionExperience(
            goal=goal,
            mission_type=record.mission_type,
            inputs=record.inputs,
            outputs=record.outputs,
            duration_ms=duration_ms,
            success=(status == "completed"),
            capabilities_used=capabilities_used or [],
            failure_reasons=failures or [],
            lessons_learned=lessons,
            tags=[status] + (capabilities_used or []),
        )
        self.repository.save_experience(exp)
        self._publish_event(MissionMemoryEvent.EXPERIENCE_CREATED, exp.to_dict())

        logger.info(f"Recorded mission '{record.mission_id}' and created distilled experience '{exp.experience_id}'")
        return record

    def find_similar_experiences(self, goal_query: str, top_k: int = 5) -> List[MissionExperience]:
        """
        Search operational experiences for AI Planner knowledge reuse.

        Returns:
            List of matching MissionExperience objects.
        """
        results = self.repository.search_experiences_by_goal(goal_query, top_k)
        if results:
            self._publish_event(MissionMemoryEvent.EXPERIENCE_RETRIEVED, {"goal_query": goal_query, "match_count": len(results)})
        return results

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        logger.info("Starting MissionMemoryService...")

    def stop(self) -> None:
        logger.info("Stopping MissionMemoryService...")

    def is_healthy(self) -> bool:
        return True

    def _publish_event(self, event: MissionMemoryEvent, data: Dict[str, Any]) -> None:
        if self.bus:
            try:
                self.bus.publish(event.value, data)
            except Exception as e:
                logger.error(f"Failed to publish mission memory event '{event.value}': {e}")
