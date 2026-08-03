from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import time


class ConflictPolicy(Enum):
    LAST_WRITE_WINS = "last_write_wins"
    TIMESTAMP_MERGE = "timestamp_merge"
    MANUAL_MERGE = "manual_merge"


@dataclass
class UserAccount:
    """User account entity for Cloud Platform."""
    user_id: str
    email: str
    password_hash: str
    is_verified: bool = True
    created_at: float = field(default_factory=time.time)


@dataclass
class DeviceSession:
    """Registered device session metadata."""
    device_id: str
    user_id: str
    device_name: str
    device_type: str  # desktop, laptop, mobile
    last_active: float = field(default_factory=time.time)
    is_active: bool = True


@dataclass
class SyncPayload:
    """Multi-device synchronization payload."""
    payload_id: str
    user_id: str
    device_id: str
    timestamp: float
    preferences: Dict[str, Any] = field(default_factory=dict)
    memory: Dict[str, Any] = field(default_factory=dict)
    knowledge: Dict[str, Any] = field(default_factory=dict)
    workflows: Dict[str, Any] = field(default_factory=dict)
    settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BackupSnapshot:
    """Backup snapshot archive metadata."""
    backup_id: str
    user_id: str
    version: str
    created_at: float = field(default_factory=time.time)
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CloudQuota:
    """Storage and API rate limit usage quota."""
    user_id: str
    used_storage_mb: float = 0.0
    max_storage_mb: float = 5000.0
    api_calls_today: int = 0
