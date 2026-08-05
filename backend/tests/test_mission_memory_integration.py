"""
Mission Memory Integration Unit, Persistence, Semantic Retrieval, Planner Lookup, and Performance Test Suite.
Tests MissionMemoryIntegrationService, MissionPersistence, MissionRetrievalEngine, MissionSummarizer, and PlannerMemoryLookup.
"""

import sys
import time
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, ".")

from memory.integration.models import (
    MissionSearchResult,
    OperationalMissionRecord,
)
from memory.integration.events import MissionMemoryIntegrationEvent
from memory.integration.configuration import MissionMemoryIntegrationConfig
from memory.integration.mission_persistence import (
    CorruptedRecordError,
    MissionPersistence,
    StorageError,
)
from memory.integration.summarization import MissionSummarizer
from memory.integration.retrieval import MissionRetrievalEngine
from memory.integration.planner_lookup import PlannerMemoryLookup
from memory.integration.mission_memory_service import MissionMemoryIntegrationService


class TestMissionMemoryIntegration(unittest.TestCase):
    """Test suite for Mission Memory Integration subsystem."""

    def setUp(self):
        self.bus = MagicMock()
        self.config = MissionMemoryIntegrationConfig()
        self.persistence = MissionPersistence()
        self.retrieval = MissionRetrievalEngine(persistence=self.persistence)
        self.lookup = PlannerMemoryLookup(retrieval_engine=self.retrieval)
        self.service = MissionMemoryIntegrationService(bus=self.bus, config=self.config, persistence=self.persistence)

    def test_mission_persistence_and_archiving(self):
        """Test persisting, retrieving, and archiving OperationalMissionRecord objects."""
        record = OperationalMissionRecord(
            user_request="Launch Notepad and type Hello",
            goal="Launch Notepad and type Hello",
            capability_usage=["launch_application", "type_text"],
            status="completed",
        )
        self.persistence.save_mission_record(record)

        loaded = self.persistence.get_mission_record(record.mission_id)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.goal, "Launch Notepad and type Hello")

        # Archive record
        self.assertTrue(self.persistence.archive_mission_record(record.mission_id))
        self.assertIsNotNone(self.persistence.get_mission_record(record.mission_id))

        # Corrupted record missing goal raises CorruptedRecordError
        bad_record = OperationalMissionRecord(mission_id="bad_123", goal="")
        with self.assertRaises(CorruptedRecordError):
            self.persistence.save_mission_record(bad_record)

    def test_multi_axis_retrieval(self):
        """Test retrieval by ID, Mission Type, Capability, Tags, Similarity, and Failure Pattern."""
        r1 = OperationalMissionRecord(
            goal="Open website and download file",
            mission_type="browser_workflow",
            capability_usage=["open_website", "download_file"],
            tags=["browser", "download"],
            status="completed",
        )
        r2 = OperationalMissionRecord(
            goal="Type text in Notepad",
            mission_type="desktop_workflow",
            capability_usage=["type_text"],
            tags=["desktop"],
            status="failed",
            verification_evidence={"reason": "UI element not found"},
        )
        self.persistence.save_mission_record(r1)
        self.persistence.save_mission_record(r2)

        # Retrieval by Capability
        caps = self.retrieval.get_by_capability("download_file")
        self.assertEqual(len(caps), 1)
        self.assertEqual(caps[0].goal, "Open website and download file")

        # Retrieval by Failure Pattern
        fails = self.retrieval.get_by_failure_pattern("not found")
        self.assertEqual(len(fails), 1)
        self.assertEqual(fails[0].goal, "Type text in Notepad")

        # Semantic Similarity Search
        sims = self.retrieval.search_similar_missions("Notepad text", top_k=5)
        self.assertGreaterEqual(len(sims), 1)
        self.assertEqual(sims[0].mission_record.goal, "Type text in Notepad")

    def test_planner_lookup_assistance(self):
        """Test PlannerMemoryLookup providing planning context assistance to AIPlanner without executing workflows."""
        r = OperationalMissionRecord(
            goal="Search Google for AI papers",
            capability_usage=["search", "extract_article"],
            lessons_learned=["Use specific query string for high precision"],
            status="completed",
        )
        self.persistence.save_mission_record(r)

        assistance = self.lookup.get_planning_context_assistance("Search Google for AI")
        self.assertGreaterEqual(assistance["similar_mission_count"], 1)
        self.assertIn("search", assistance["recommended_capabilities"])
        self.assertIn("Use specific query string for high precision", assistance["lessons_learned"])

    def test_end_to_end_service_and_events(self):
        """Test MissionMemoryIntegrationService listening to workflow completion and storing operational records."""
        self.service.start()

        # Simulate workflow completion event
        event_payload = {
            "goal": "Automated Web Scraping Mission",
            "status": "completed",
            "completed_tasks": ["open_website", "extract_table"],
            "verification_result": {"verified": True},
            "recovery_attempts": 1,
        }
        self.service._on_workflow_completed(event_payload)

        # Check records stored
        records = self.persistence.list_all_records()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].goal, "Automated Web Scraping Mission")

        published = [call[0][0] for call in self.bus.publish.call_args_list]
        self.assertIn("mission_stored", published)

    def test_performance(self):
        """Performance stress test storing and searching 100 operational mission records."""
        start_time = time.time()
        for i in range(100):
            r = OperationalMissionRecord(
                goal=f"Batch Mission Goal {i} with capability action",
                capability_usage=["action_cap"],
                status="completed" if i % 2 == 0 else "failed",
            )
            self.persistence.save_mission_record(r)

        store_time = time.time() - start_time
        self.assertLess(store_time, 1.0)

        search_start = time.time()
        res = self.retrieval.search_similar_missions("Batch Mission Goal 50", top_k=10)
        search_time = time.time() - search_start

        self.assertLess(search_time, 0.1)
        self.assertEqual(len(res), 10)


if __name__ == "__main__":
    unittest.main()
