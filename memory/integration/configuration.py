from dataclasses import dataclass


@dataclass
class MissionMemoryIntegrationConfig:
    retention_policy: str = "retain_forever"
    max_mission_size_bytes: int = 10485760
    embedding_provider: str = "tfidf_vectorizer"
    archive_strategy: str = "compress_old_records"
    top_k_planner_matches: int = 5
