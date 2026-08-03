import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger("AURA.Agent.History")


class AgentHistory:
    """
    Logs workflow timeline events, task execution graphs, and execution performance metrics.
    """

    def __init__(self):
        self._timeline: List[Dict[str, Any]] = []

    def log_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Log a timeline event."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details
        }
        self._timeline.append(entry)
        logger.info(f"Timeline [{event_type}]: {details}")

    def get_timeline(self) -> List[Dict[str, Any]]:
        """Retrieve recorded execution timeline."""
        return list(self._timeline)

    def summary(self) -> Dict[str, Any]:
        """Generate high-level summary of history timeline."""
        return {
            "total_events": len(self._timeline),
            "events": self.get_timeline()
        }
