"""
Browser Event Subscription Manager.
Registers and manages subscriptions between the AURA EventBus and subsystem listeners.
"""

import logging
from typing import Any, Callable, Dict, List, Optional

from browser.events.listeners import (
    KnowledgeEventListener,
    MemoryEventListener,
    VisionEventListener,
    WorkflowEventListener,
)

logger = logging.getLogger("AURA.Browser.Events.Subscriptions")


class BrowserEventSubscriptionManager:
    """
    Manages EventBus subscriptions for Workflow, Memory, Knowledge, and Vision listeners.
    """

    def __init__(self, bus: Any = None):
        self.bus = bus
        self.workflow_listener = WorkflowEventListener()
        self.memory_listener = MemoryEventListener()
        self.knowledge_listener = KnowledgeEventListener()
        self.vision_listener = VisionEventListener()

        self._subscriptions: List[Dict[str, Any]] = []

    def setup_subscriptions(
        self,
        workflow_engine: Any = None,
        memory_engine: Any = None,
        knowledge_engine: Any = None,
        vision_engine: Any = None,
    ) -> None:
        """
        Wire subsystem listeners to their respective engine references and subscribe to EventBus topics.
        """
        if workflow_engine:
            self.workflow_listener.workflow_engine_ref = workflow_engine
        if memory_engine:
            self.memory_listener.memory_engine_ref = memory_engine
        if knowledge_engine:
            self.knowledge_listener.knowledge_engine_ref = knowledge_engine
        if vision_engine:
            self.vision_listener.vision_engine_ref = vision_engine

        if not self.bus:
            logger.warning("EventBus is None. Subscriptions configured locally without bus binding.")
            return

        # Subscribe Workflow Listener
        workflow_topics = [
            "navigation_started", "navigation_completed", "navigation_failed",
            "page_loaded", "page_reloaded", "click_completed", "text_typed",
            "form_submitted", "file_uploaded", "file_downloaded", "action_verified"
        ]
        for topic in workflow_topics:
            self.subscribe(topic, self.workflow_listener.on_event)

        # Subscribe Memory Listener
        memory_topics = ["article_extracted", "form_submitted", "file_downloaded", "download_completed"]
        for topic in memory_topics:
            self.subscribe(topic, self.memory_listener.on_event)

        # Subscribe Knowledge Listener
        knowledge_topics = ["article_extracted", "table_extracted"]
        for topic in knowledge_topics:
            self.subscribe(topic, self.knowledge_listener.on_event)

        # Subscribe Vision Listener
        vision_topics = ["screenshot_created", "ui_changed"]
        for topic in vision_topics:
            self.subscribe(topic, self.vision_listener.on_event)

        logger.info("Subsystem event subscriptions registered successfully")

    def subscribe(self, event_type: str, handler: Callable[[Dict[str, Any]], None]) -> None:
        """Subscribe a handler callback to an event_type topic."""
        if self.bus:
            try:
                if hasattr(self.bus, "subscribe"):
                    self.bus.subscribe(event_type, handler)
                    self._subscriptions.append({"event_type": event_type, "handler": handler})
                    logger.debug(f"Subscribed handler to EventBus topic '{event_type}'")
            except Exception as e:
                logger.error(f"Failed to subscribe to EventBus topic '{event_type}': {e}")

    def clear(self) -> None:
        """Clear registered subscriptions."""
        self._subscriptions.clear()
        logger.debug("Subsystem event subscriptions cleared")
