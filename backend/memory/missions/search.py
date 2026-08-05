"""
Mission Multi-Index & Semantic Vector Search Engine.
Supports searching experiences by Goal, Capability, Failure, Tags, and Embedding Vector Similarity.
"""

import logging
from typing import List, Optional

from memory.missions.embeddings import MissionEmbeddingEngine
from memory.missions.experience_store import ExperienceStore
from memory.missions.models import MissionExperience

logger = logging.getLogger("AURA.Memory.Missions.Search")


class MissionSearchEngine:
    """
    Search engine for retrieving relevant operational experiences.
    """

    def __init__(self, experience_store: ExperienceStore):
        self.exp_store = experience_store
        self.embedding_engine = MissionEmbeddingEngine()

    def search_by_goal(self, goal_query: str, top_k: int = 5) -> List[MissionExperience]:
        """
        Search experiences by goal string similarity or embedding similarity.
        """
        query_vec = self.embedding_engine.generate_embedding(goal_query)
        all_exps = self.exp_store.list_all()

        scored = []
        for exp in all_exps:
            if not exp.embedding:
                exp.embedding = self.embedding_engine.generate_embedding(exp.goal)
            sim = self.embedding_engine.compute_similarity(query_vec, exp.embedding)
            scored.append((sim, exp))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = [exp for sim, exp in scored[:top_k] if sim > 0.1]
        logger.info(f"Goal search '{goal_query}' returned {len(results)} matches")
        return results

    def search_by_capability(self, capability: str) -> List[MissionExperience]:
        """Search experiences that used specific capability."""
        all_exps = self.exp_store.list_all()
        return [e for e in all_exps if capability in e.capabilities_used]

    def search_by_failure(self, failure_keyword: str) -> List[MissionExperience]:
        """Search experiences with matching failure reasons."""
        all_exps = self.exp_store.list_all()
        kw = failure_keyword.lower()
        return [e for e in all_exps if any(kw in f.lower() for f in e.failure_reasons)]

    def search_by_tags(self, tags: List[str]) -> List[MissionExperience]:
        """Search experiences matching any specified tags."""
        tag_set = set(t.lower() for t in tags)
        all_exps = self.exp_store.list_all()
        return [e for e in all_exps if any(t.lower() in tag_set for t in e.tags)]
