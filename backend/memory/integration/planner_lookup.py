"""
Planner Memory Lookup.
Exposes read-only operational mission experience search interface to the AI Planner Engine.
Enforces:
The Planner MAY use Mission Memory for planning, but Mission Memory MUST NEVER execute workflows.
"""

import logging
from typing import Any, Dict, List, Optional

from memory.integration.models import MissionSearchResult
from memory.integration.retrieval import MissionRetrievalEngine

logger = logging.getLogger("AURA.Memory.Integration.PlannerLookup")


class PlannerMemoryLookup:
    """
    Read-only operational knowledge lookup for AI Planner DAG task graph optimization.
    """

    def __init__(self, retrieval_engine: Optional[MissionRetrievalEngine] = None):
        self.retrieval_engine = retrieval_engine or MissionRetrievalEngine()

    def get_planning_context_assistance(self, user_request: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Query operational mission memory to assist AI Planner during task decomposition.

        Args:
            user_request: Natural language prompt requested by user.
            top_k: Number of similar operational experiences to return.

        Returns:
            Dictionary containing relevant past capabilities, successful sub-graphs, and failure warnings.
        """
        logger.info(f"AI Planner querying Mission Memory assistance for request: '{user_request}'...")

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
