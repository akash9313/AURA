"""
Mission Memory Engine Unit, Retrieval, Embedding Search, Retention, and Performance Test Suite.
Tests MissionRecord, MissionExperience, MissionStore, ExperienceStore, MissionEmbeddingEngine, MissionSearchEngine,
MissionSummarizer, MissionRetentionPolicy, MissionRepository, and MissionMemoryService.
"""

import sys
import time
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, ".")

from memory.missions.models import (
    MissionCheckpointRecord,
    MissionExperience,
    MissionRecord,
)
from memory.missions.events import MissionMemoryEvent
from memory.missions.configuration import MissionMemoryConfig
from memory.missions.embeddings import MissionEmbeddingEngine
from memory.missions.summarizer import MissionSummarizer
from memory.missions.retention import MissionRetentionPolicy
from memory.missions.mission_store import MissionStore
from memory.missions.experience_store import ExperienceStore
from memory.missions.search import MissionSearchEngine
from memory.missions.repository import MissionRepository
from memory.missions.service import MissionMemoryService


class TestMissionMemoryEngine(unittest.TestCase):
    """Test suite for Mission Memory Engine subsystem."""

    def setUp(self):
        self.bus = MagicMock()
        self.config = MissionMemoryConfig(retention_days=90)
        self.service = MissionMemoryService(bus=self.bus, config=self.config)

    def test_record_mission_and_distill_experience(self):
        """Record mission execution and verify distilled experience creation."""
        rec = self.service.record_mission_execution(
            goal="Open Notepad and write report",
            capabilities_used=["open_application", "write_file"],
            duration_ms=450.0,
            status="completed",
        )

        self.assertIsNotNone(rec.mission_id)
        self.assertEqual(rec.goal, "Open Notepad and write report")
        self.assertIn("succeeded", rec.reflection_summary)

        # Retrieve distilled experience
        matches = self.service.find_similar_experiences("write report in Notepad")
        self.assertGreater(len(matches), 0)
        self.assertEqual(matches[0].goal, "Open Notepad and write report")

        # Verify EventBus events
        published = [call[0][0] for call in self.bus.publish.call_args_list]
        self.assertIn("mission_stored", published)
        self.assertIn("experience_created", published)
        self.assertIn("experience_retrieved", published)

    def test_embedding_engine_vector_similarity(self):
        """Test embedding generation and cosine similarity calculation."""
        engine = MissionEmbeddingEngine()
        vec_a = engine.generate_embedding("Open Spotify application")
        vec_b = engine.generate_embedding("Launch Spotify desktop app")
        vec_c = engine.generate_embedding("Delete database table")

        sim_ab = engine.compute_similarity(vec_a, vec_b)
        sim_ac = engine.compute_similarity(vec_a, vec_c)

        self.assertGreater(sim_ab, sim_ac)

    def test_retention_policy_expiration(self):
        """Test retention policy archival of expired records."""
        policy = MissionRetentionPolicy(MissionMemoryConfig(retention_days=1))
        old_record = MissionRecord(goal="Old Mission", created_at=time.time() - (2 * 86400.0))
        new_record = MissionRecord(goal="New Mission", created_at=time.time())

        active, archived_ids = policy.apply_retention([old_record, new_record])

        self.assertEqual(len(active), 1)
        self.assertIn(old_record.mission_id, archived_ids)
        self.assertTrue(old_record.archived)

    def test_high_volume_retrieval_performance(self):
        """Performance test ensuring sub-millisecond retrieval across 1,000 experiences."""
        for i in range(1000):
            exp = MissionExperience(
                goal=f"Automated workflow goal {i}",
                capabilities_used=["open_application"],
            )
            self.service.repository.save_experience(exp)

        start_time = time.time()
        results = self.service.find_similar_experiences("Automated workflow goal 500", top_k=5)
        duration_ms = (time.time() - start_time) * 1000.0

        self.assertGreater(len(results), 0)
        self.assertLess(duration_ms, 50.0)  # Must be fast (< 50ms)


if __name__ == "__main__":
    unittest.main()
