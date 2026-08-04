"""
Standardized Browser Event Models and Metadata.
Every browser event contains structured metadata (Event ID, Timestamp, Correlation ID,
Workflow ID, Session ID, Browser ID, Page ID, Duration, Status) and a custom Payload.
"""

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class BrowserEventMetadata:
    """Standardized metadata attached to every browser event."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    correlation_id: Optional[str] = None
    workflow_id: Optional[str] = None
    session_id: Optional[str] = None
    browser_id: Optional[str] = None
    page_id: Optional[str] = None
    duration_ms: float = 0.0
    status: str = "success"  # 'success', 'failed', 'retry'

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "correlation_id": self.correlation_id,
            "workflow_id": self.workflow_id,
            "session_id": self.session_id,
            "browser_id": self.browser_id,
            "page_id": self.page_id,
            "duration_ms": self.duration_ms,
            "status": self.status,
        }


@dataclass
class BrowserEventMessage:
    """Complete structured browser event message emitted onto the EventBus."""
    event_type: str
    metadata: BrowserEventMetadata
    payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "metadata": self.metadata.to_dict(),
            "payload": self.payload,
        }
