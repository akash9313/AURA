"""
AURA Mission Memory Integration Subsystem (`backend/memory/integration/`).
Persists completed workflows as operational knowledge independent from conversation memory,
supporting semantic retrieval and AI Planner assistance.
"""

from memory.integration.configuration import MissionMemoryIntegrationConfig
from memory.integration.events import MissionMemoryIntegrationEvent
from memory.integration.mission_memory_service import MissionMemoryIntegrationService
from memory.integration.mission_persistence import (
    CorruptedRecordError,
    MissionPersistence,
    StorageError,
)
from memory.integration.models import MissionSearchResult, OperationalMissionRecord
from memory.integration.planner_lookup import PlannerMemoryLookup
from memory.integration.retrieval import MissionRetrievalEngine
from memory.integration.summarization import MissionSummarizer

__all__ = [
    "MissionMemoryIntegrationService",
    "MissionPersistence",
    "MissionSummarizer",
    "MissionRetrievalEngine",
    "PlannerMemoryLookup",
    "MissionMemoryIntegrationConfig",
    "OperationalMissionRecord",
    "MissionSearchResult",
    "MissionMemoryIntegrationEvent",
    "StorageError",
    "CorruptedRecordError",
]
