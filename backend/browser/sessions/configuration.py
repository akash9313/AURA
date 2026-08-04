import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SessionConfig:
    """Configurable infrastructure settings for Browser Session Management."""
    session_timeout_seconds: float = 3600.0  # 1 hour
    auto_save_interval_seconds: float = 300.0  # 5 minutes
    persistence_path: str = os.path.join("data", "sessions")
    max_active_sessions: int = 20
    storage_quota_mb: float = 100.0
    encryption_enabled: bool = False
    encryption_key: Optional[str] = None
