"""
Core Browser Event Dispatcher.
Orchestrates event publishing, subsystem subscriptions, structured logging, and event replaying.
Ensures minimal latency overhead and thread-safe execution.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from browser.events.browser_events import BrowserEventType
from browser.events.event_logger import BrowserEventLogger
from browser.events.event_models import BrowserEventMessage
from browser.events.publishers import BrowserEventPublisher
from browser.events.subscriptions import BrowserEventSubscriptionManager

logger = logging.getLogger("AURA.Browser.Events.Dispatcher")


class BrowserEventDispatcher:
    """
    Central Browser Subsystem Event Dispatcher.
    All browser operations emit events through this dispatcher.
    """

    def __init__(self, bus: Any = None):
        self.bus = bus
        self.publisher = BrowserEventPublisher(bus=bus)
        self.subscriptions = BrowserEventSubscriptionManager(bus=bus)
        self.logger_buffer = BrowserEventLogger()

        logger.info("BrowserEventDispatcher initialized")

    def dispatch(
        self,
        event_type: Union[BrowserEventType, str],
        payload: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        session_id: Optional[str] = None,
        browser_id: Optional[str] = None,
        page_id: Optional[str] = None,
        duration_ms: float = 0.0,
        status: str = "success",
    ) -> Optional[BrowserEventMessage]:
        """
        Dispatch a browser event: constructs metadata, logs to buffer, and emits to EventBus.

        Returns:
            Dispatched BrowserEventMessage object.
        """
        # Publish to EventBus
        msg = self.publisher.publish_event(
            event_type=event_type,
            payload=payload,
            correlation_id=correlation_id,
            workflow_id=workflow_id,
            session_id=session_id,
            browser_id=browser_id,
            page_id=page_id,
            duration_ms=duration_ms,
            status=status,
        )

        if msg:
            # Log to in-memory replay buffer
            self.logger_buffer.log_event(msg)

        return msg

    def register_subsystems(
        self,
        workflow_engine: Any = None,
        memory_engine: Any = None,
        knowledge_engine: Any = None,
        vision_engine: Any = None,
    ) -> None:
        """Register subsystem engine references for event listening."""
        self.subscriptions.setup_subscriptions(
            workflow_engine=workflow_engine,
            memory_engine=memory_engine,
            knowledge_engine=knowledge_engine,
            vision_engine=vision_engine,
        )

    def replay_events(
        self, handler_func: Any, workflow_id: Optional[str] = None, session_id: Optional[str] = None
    ) -> int:
        """Replay historical events matching query."""
        return self.logger_buffer.replay_events(handler_func, workflow_id=workflow_id, session_id=session_id)

    def get_logs(self, limit: Optional[int] = None) -> str:
        """Export JSON event logs."""
        return self.logger_buffer.export_json_logs(limit=limit)
