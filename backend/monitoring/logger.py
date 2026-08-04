import json
import logging
import time
from typing import Any, Dict, Optional

logger = logging.getLogger("AURA.Monitoring.Logger")


class StructuredLogger:
    """Structured JSON Logger with Trace Correlation IDs."""

    def log_event(
        self,
        component: str,
        message: str,
        correlation_id: Optional[str] = None,
        severity: str = "INFO",
        duration_ms: Optional[float] = None,
        extra: Optional[Dict[str, Any]] = None
    ) -> str:
        payload = {
            "timestamp": time.time(),
            "component": component,
            "message": message,
            "correlation_id": correlation_id or "nocorr",
            "severity": severity,
            "duration_ms": duration_ms,
            "extra": extra or {}
        }
        formatted = json.dumps(payload)
        logger.info(formatted)
        return formatted
