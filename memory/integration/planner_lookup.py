import logging
from typing import Any, Dict, List, Optional

from memory.integration.models import MissionSearchResult
from memory.integration.retrieval import MissionRetrievalEngine

logger = logging.getLogger("AURA.Memory.Integration.PlannerLookup")


class PlannerMemoryLookup:
    def __init__(self, retrieval_engine: Optional[MissionRetrievalEngine] = None):
        self.retrieval_engine = retrieval_engine or MissionRetrievalEngine()

    def get_planning_context_assistance(self, user_request: str, top_k: int = 3) -> Dict[str, Any]:
        matches: List[MissionSearchResult] = self.retrieval_engine.search_similar_missions(user_request, top_k=top_k)

        recommended_capabilities: List[str] = []
        failure_warnings: List[str] = []
        lessons: List[str] = []

        for match in matches:
            record = match.mission_record
            for cap in record.capability_usage:
                if cap not in recommended_capabilities:
                    recommended_capabilities.append(cap)

            if record.status == "failed":
                failure_warnings.append(f"Past mission '{record.goal}' failed: {record.verification_evidence}")

            for lesson in record.lessons_learned:
                if lesson not in lessons:
                    lessons.append(lesson)

        return {
            "similar_mission_count": len(matches),
            "recommended_capabilities": recommended_capabilities,
            "failure_warnings": failure_warnings,
            "lessons_learned": lessons,
            "historical_matches": [m.to_dict() for m in matches],
        }
