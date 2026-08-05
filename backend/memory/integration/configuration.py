"""
Mission Memory Integration Configuration.
Configures retention policies, max mission sizes, embedding providers, and archive strategies.
"""

from dataclasses import dataclass


@dataclass
class MissionMemoryIntegrationConfig:
    """Configuration parameters for Mission Memory Integration Subsystem."""
    retention_policy: str = "retain_forever"
    max_mission_size_bytes: int = 10485760  # 10 MB limit
    embedding_provider: str = "tfidf_vectorizer"
    archive_strategy: str = "compress_old_records"
    top_k_planner_matches: int = 5
