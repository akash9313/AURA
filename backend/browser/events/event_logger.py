"""
Structured Browser Event Logger.
Maintains an in-memory ring buffer of browser events for auditing, debugging, filtering, and event replay.
"""

import json
import logging
from collections import deque
from typing import Any, Dict, List, Optional, Union

from browser.events.event_models import BrowserEventMessage

logger = logging.getLogger("AURA.Browser.Events.Logger")


class BrowserEventLogger:
    """
    Structured in-memory event logger and replay buffer.
    """

    def __init__(self, max_capacity: int = 1000):
        self.max_capacity = max_capacity
        self._history: deque = deque(maxlen=max_capacity)

    def log_event(self, message: BrowserEventMessage) -> None:
        """Record an event message into history buffer."""
        self._history.append(message)
        logger.debug(f"Event logged: {message.event_type} (ID: {message.metadata.event_id})")

    def get_events(
        self,
        event_type: Optional[str] = None,
        workflow_id: Optional[str] = None,
        session_id: Optional[str] = None,
        page_id: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[BrowserEventMessage]:
        """
        Filter event history buffer.

        Returns:
            List of matching BrowserEventMessage objects.
        """
        results = []
        for msg in reversed(self._history):
            if event_type and msg.event_type != event_type:
                continue
            if workflow_id and msg.metadata.workflow_id != workflow_id:
                continue
            if session_id and msg.metadata.session_id != session_id:
                continue
            if page_id and msg.metadata.page_id != page_id:
                continue

            results.append(msg)
            if limit and len(results) >= limit:
                break

        return list(reversed(results))

    def replay_events(
        self,
        handler_func: Any,
        workflow_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> int:
        """
        Replay matching historical events through a handler callable.

        Returns:
            Count of replayed events.
        """
        matching = self.get_events(workflow_id=workflow_id, session_id=session_id)
        replayed = 0
        for msg in matching:
            try:
                handler_func(msg)
                replayed += 1
            except Exception as e:
                logger.error(f"Event replay handler error for '{msg.event_type}': {e}")
        logger.info(f"Replayed {replayed} browser events")
        return replayed

    def export_json_logs(self, limit: Optional[int] = None) -> str:
        """Export history buffer as a JSON string."""
        events = self.get_events(limit=limit)
        dict_list = [e.to_dict() for e in events]
        return json.dumps(dict_list, indent=2)

    def clear(self) -> None:
        """Clear historical event log buffer."""
        self._history.clear()
        logger.debug("Browser event log buffer cleared")
