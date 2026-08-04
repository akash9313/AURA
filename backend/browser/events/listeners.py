"""
Subsystem Decoupled Event Listeners.
Implements specialized listeners for Workflow Engine, Memory Engine, Knowledge Engine, and Vision Engine integration.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("AURA.Browser.Events.Listeners")


class WorkflowEventListener:
    """
    Subscribes to browser events and advances Workflow Engine state.
    Decoupled via EventBus.
    """

    def __init__(self, workflow_engine_ref: Any = None):
        self.workflow_engine_ref = workflow_engine_ref
        self.processed_events: List[Dict[str, Any]] = []

    def on_event(self, event_data: Dict[str, Any]) -> None:
        """Handle incoming browser event."""
        evt_type = event_data.get("event_type")
        payload = event_data.get("payload", {})
        metadata = event_data.get("metadata", {})

        self.processed_events.append(event_data)
        logger.info(f"[WorkflowEventListener] Received '{evt_type}' (Workflow ID: {metadata.get('workflow_id')})")

        if self.workflow_engine_ref and hasattr(self.workflow_engine_ref, "on_browser_event"):
            try:
                self.workflow_engine_ref.on_browser_event(event_data)
            except Exception as e:
                logger.error(f"WorkflowEngine callback error: {e}")


class MemoryEventListener:
    """
    Subscribes to ARTICLE_EXTRACTED, FORM_SUBMITTED, DOWNLOAD_COMPLETED.
    Passes extracted information to Memory Engine.
    """

    def __init__(self, memory_engine_ref: Any = None):
        self.memory_engine_ref = memory_engine_ref
        self.memory_records: List[Dict[str, Any]] = []

    def on_event(self, event_data: Dict[str, Any]) -> None:
        evt_type = event_data.get("event_type")
        payload = event_data.get("payload", {})

        if evt_type in ("article_extracted", "form_submitted", "download_completed"):
            record = {
                "source": "browser_subsystem",
                "event_type": evt_type,
                "data": payload,
            }
            self.memory_records.append(record)
            logger.info(f"[MemoryEventListener] Recorded memory item for '{evt_type}'")

            if self.memory_engine_ref and hasattr(self.memory_engine_ref, "store_memory"):
                try:
                    self.memory_engine_ref.store_memory(record)
                except Exception as e:
                    logger.error(f"MemoryEngine callback error: {e}")


class KnowledgeEventListener:
    """
    Subscribes to ARTICLE_EXTRACTED, TABLE_EXTRACTED.
    Passes structured article and table knowledge to Knowledge Engine.
    """

    def __init__(self, knowledge_engine_ref: Any = None):
        self.knowledge_engine_ref = knowledge_engine_ref
        self.knowledge_records: List[Dict[str, Any]] = []

    def on_event(self, event_data: Dict[str, Any]) -> None:
        evt_type = event_data.get("event_type")
        payload = event_data.get("payload", {})

        if evt_type in ("article_extracted", "table_extracted"):
            record = {
                "source": "browser_subsystem",
                "event_type": evt_type,
                "content": payload,
            }
            self.knowledge_records.append(record)
            logger.info(f"[KnowledgeEventListener] Ingested knowledge item for '{evt_type}'")

            if self.knowledge_engine_ref and hasattr(self.knowledge_engine_ref, "add_knowledge"):
                try:
                    self.knowledge_engine_ref.add_knowledge(record)
                except Exception as e:
                    logger.error(f"KnowledgeEngine callback error: {e}")


class VisionEventListener:
    """
    Subscribes to SCREENSHOT_CREATED, UI_CHANGED.
    Passes visual snapshots to Vision Engine.
    """

    def __init__(self, vision_engine_ref: Any = None):
        self.vision_engine_ref = vision_engine_ref
        self.vision_records: List[Dict[str, Any]] = []

    def on_event(self, event_data: Dict[str, Any]) -> None:
        evt_type = event_data.get("event_type")
        payload = event_data.get("payload", {})

        if evt_type in ("screenshot_created", "ui_changed"):
            record = {
                "source": "browser_subsystem",
                "event_type": evt_type,
                "image_data": payload,
            }
            self.vision_records.append(record)
            logger.info(f"[VisionEventListener] Processed vision snapshot for '{evt_type}'")

            if self.vision_engine_ref and hasattr(self.vision_engine_ref, "analyze_ui"):
                try:
                    self.vision_engine_ref.analyze_ui(record)
                except Exception as e:
                    logger.error(f"VisionEngine callback error: {e}")
