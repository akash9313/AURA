import logging
from typing import Any, Dict, List, Optional

from core.service import Service
from memory.integration.configuration import MissionMemoryIntegrationConfig
from memory.integration.events import MissionMemoryIntegrationEvent
from memory.integration.mission_persistence import MissionPersistence
from memory.integration.models import MissionSearchResult, OperationalMissionRecord
from memory.integration.planner_lookup import PlannerMemoryLookup
from memory.integration.retrieval import MissionRetrievalEngine
from memory.integration.summarization import MissionSummarizer

logger = logging.getLogger("AURA.Memory.Integration.Service")


class MissionMemoryIntegrationService(Service):
    def __init__(
        self,
        bus: Any = None,
        config: Optional[MissionMemoryIntegrationConfig] = None,
        persistence: Optional[MissionPersistence] = None,
    ):
        super().__init__(bus)
        self.config = config or MissionMemoryIntegrationConfig()
        self.persistence = persistence or MissionPersistence()
        self.summarizer = MissionSummarizer()
        self.retrieval_engine = MissionRetrievalEngine(persistence=self.persistence)
        self.planner_lookup = PlannerMemoryLookup(retrieval_engine=self.retrieval_engine)

    def start(self) -> None:
        if self.bus:
            self.bus.subscribe("workflow_completed", self._on_workflow_completed)
            self.bus.subscribe("MISSION_COMPLETED", self._on_workflow_completed)
            self.bus.subscribe("MISSION_FAILED", self._on_workflow_completed)

    def stop(self) -> None:
        pass

    def is_healthy(self) -> bool:
        return True

    def _on_workflow_completed(self, payload: Any) -> None:
        if not isinstance(payload, dict):
            return

        goal = payload.get("goal", payload.get("user_request", "Unknown Mission"))
        status = payload.get("status", "completed")

        self.store_operational_mission(
            user_request=goal,
            goal=goal,
            status=status,
            task_graph=payload.get("task_graph", {}),
            execution_timeline=payload.get("execution_timeline", []),
            capability_usage=payload.get("completed_tasks", payload.get("capabilities_used", [])),
            verification_evidence=payload.get("verification_result", payload.get("evidence", {})),
            recovery_attempts=payload.get("recovery_attempts", 0),
            reflection_report=payload.get("reflection_report", {}),
        )

    def store_operational_mission(
        self,
        user_request: str,
        goal: str,
        status: str = "completed",
        task_graph: Dict[str, Any] = None,
        execution_timeline: List[Dict[str, Any]] = None,
        capability_usage: List[str] = None,
        verification_evidence: Dict[str, Any] = None,
        recovery_attempts: int = 0,
        reflection_report: Dict[str, Any] = None,
    ) -> OperationalMissionRecord:
        summary_str, lessons = self.summarizer.summarize_mission(
            goal=goal,
            status=status,
            capabilities_used=capability_usage or [],
            verification_evidence=verification_evidence or {},
            reflection_report=reflection_report or {},
            recovery_attempts=recovery_attempts,
        )

        record = OperationalMissionRecord(
            user_request=user_request,
            goal=goal,
            status=status,
            task_graph=task_graph or {},
            execution_timeline=execution_timeline or [],
            capability_usage=capability_usage or [],
            verification_evidence=verification_evidence or {},
            recovery_attempts=recovery_attempts,
            reflection_report=reflection_report or {},
            lessons_learned=lessons,
            tags=[status] + (capability_usage or []),
        )

        self.persistence.save_mission_record(record)
        self._publish_event(MissionMemoryIntegrationEvent.MISSION_STORED, record.to_dict())

        return record

    def search_similar_missions_for_planner(self, goal_query: str, top_k: int = 5) -> List[MissionSearchResult]:
        matches = self.retrieval_engine.search_similar_missions(goal_query, top_k=top_k)
        if matches and self.bus:
            self._publish_event(MissionMemoryIntegrationEvent.SIMILAR_MISSIONS_FOUND, {
                "goal_query": goal_query,
                "match_count": len(matches),
            })
        return matches

    def _publish_event(self, event: MissionMemoryIntegrationEvent, data: Dict[str, Any]) -> None:
        if self.bus:
            try:
                self.bus.publish(event.value, data)
            except Exception as e:
                logger.error(f"Failed to publish mission memory integration event '{event.value}': {e}")
