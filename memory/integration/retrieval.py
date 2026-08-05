import logging
from typing import List, Optional

from memory.integration.mission_persistence import MissionPersistence
from memory.integration.models import MissionSearchResult, OperationalMissionRecord

logger = logging.getLogger("AURA.Memory.Integration.Retrieval")


class MissionRetrievalEngine:
    def __init__(self, persistence: Optional[MissionPersistence] = None):
        self.persistence = persistence or MissionPersistence()

    def get_by_id(self, mission_id: str) -> Optional[OperationalMissionRecord]:
        return self.persistence.get_mission_record(mission_id)

    def get_by_mission_type(self, mission_type: str) -> List[OperationalMissionRecord]:
        records = self.persistence.list_all_records()
        return [r for r in records if r.mission_type.lower() == mission_type.lower()]

    def get_by_capability(self, capability_name: str) -> List[OperationalMissionRecord]:
        records = self.persistence.list_all_records()
        return [r for r in records if capability_name in r.capability_usage]

    def get_by_tags(self, tags: List[str]) -> List[OperationalMissionRecord]:
        records = self.persistence.list_all_records()
        matching = []
        for r in records:
            if any(tag in r.tags for tag in tags):
                matching.append(r)
        return matching

    def search_similar_missions(self, goal_query: str, top_k: int = 5) -> List[MissionSearchResult]:
        records = self.persistence.list_all_records()
        results: List[MissionSearchResult] = []

        query_terms = set(goal_query.lower().split())

        for r in records:
            goal_terms = set(r.goal.lower().split())
            if not query_terms or not goal_terms:
                continue

            intersection = query_terms.intersection(goal_terms)
            score = len(intersection) / float(len(query_terms.union(goal_terms)))

            if score > 0.0 or goal_query.lower() in r.goal.lower():
                final_score = max(score, 0.5 if goal_query.lower() in r.goal.lower() else score)
                results.append(MissionSearchResult(
                    mission_record=r,
                    similarity_score=final_score,
                    matched_capabilities=r.capability_usage,
                ))

        results.sort(key=lambda res: res.similarity_score, reverse=True)
        return results[:top_k]

    def get_by_failure_pattern(self, failure_keyword: str) -> List[OperationalMissionRecord]:
        records = self.persistence.list_all_records()
        matching = []
        for r in records:
            if r.status == "failed":
                ev_str = str(r.verification_evidence).lower()
                if failure_keyword.lower() in ev_str or failure_keyword.lower() in r.goal.lower():
                    matching.append(r)
        return matching
