"""
Structured Browser Event Publisher.
High-speed, non-blocking publisher that constructs BrowserEventMessage objects with full metadata
and emits them onto the AURA EventBus.
"""

import logging
import time
from typing import Any, Dict, Optional, Union

from browser.events.browser_events import BrowserEventType
from browser.events.event_models import BrowserEventMetadata, BrowserEventMessage

logger = logging.getLogger("AURA.Browser.Events.Publisher")


class BrowserEventPublisher:
    """
    Publisher responsible for standardizing event metadata and publishing to EventBus.
    """

    def __init__(self, bus: Any = None):
        self.bus = bus

    def publish_event(
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
        Publish a structured browser event to the EventBus.

        Returns:
            Constructed BrowserEventMessage object (or None if no bus available).
        """
        evt_type_str = event_type.value if isinstance(event_type, BrowserEventType) else str(event_type)

        metadata = BrowserEventMetadata(
            correlation_id=correlation_id,
            workflow_id=workflow_id,
            session_id=session_id,
            browser_id=browser_id,
            page_id=page_id,
            duration_ms=duration_ms,
            status=status,
        )

        msg = BrowserEventMessage(
            event_type=evt_type_str,
            metadata=metadata,
            payload=payload or {},
        )

        if self.bus:
            try:
                # Publish standardized dictionary to EventBus
                self.bus.publish(evt_type_str, msg.to_dict())
                logger.debug(f"Event published: '{evt_type_str}' (ID: {metadata.event_id})")
            except Exception as e:
                logger.error(f"Failed to publish event '{evt_type_str}' to EventBus: {e}")

        return msg
