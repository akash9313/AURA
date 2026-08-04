"""
Browser Events Subsystem & Workflow Integration Unit and Integration Tests.
Covers: event models, metadata serialization, dispatcher, publisher, event logger, replay buffer,
and decoupled subsystem listeners for Workflow, Memory, Knowledge, and Vision Engines.
"""

import json
import sys
import time
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, ".")

from browser.events.browser_events import BrowserEvent, BrowserEventType
from browser.events.event_models import BrowserEventMetadata, BrowserEventMessage
from browser.events.event_logger import BrowserEventLogger
from browser.events.publishers import BrowserEventPublisher
from browser.events.listeners import (
    KnowledgeEventListener,
    MemoryEventListener,
    VisionEventListener,
    WorkflowEventListener,
)
from browser.events.subscriptions import BrowserEventSubscriptionManager
from browser.events.event_dispatcher import BrowserEventDispatcher


# ==============================================================================
# Model & Metadata Tests
# ==============================================================================

class TestEventModels(unittest.TestCase):
    """Tests for BrowserEventMetadata and BrowserEventMessage."""

    def test_metadata_creation_and_dict(self):
        meta = BrowserEventMetadata(
            workflow_id="wf_101",
            session_id="sess_202",
            page_id="page_303",
            duration_ms=12.5,
            status="success",
        )
        d = meta.to_dict()
        self.assertIsNotNone(d["event_id"])
        self.assertEqual(d["workflow_id"], "wf_101")
        self.assertEqual(d["session_id"], "sess_202")
        self.assertEqual(d["page_id"], "page_303")
        self.assertEqual(d["duration_ms"], 12.5)

    def test_event_message_serialization(self):
        meta = BrowserEventMetadata(workflow_id="wf_1")
        msg = BrowserEventMessage(
            event_type=BrowserEventType.PAGE_LOADED.value,
            metadata=meta,
            payload={"url": "https://example.com", "title": "Example"},
        )
        d = msg.to_dict()
        self.assertEqual(d["event_type"], "page_loaded")
        self.assertEqual(d["payload"]["url"], "https://example.com")


# ==============================================================================
# Publisher & Dispatcher Tests
# ==============================================================================

class TestBrowserEventPublisher(unittest.TestCase):
    """Tests for BrowserEventPublisher."""

    def test_publish_event_with_bus(self):
        bus = MagicMock()
        publisher = BrowserEventPublisher(bus=bus)

        msg = publisher.publish_event(
            BrowserEventType.PAGE_LOADED,
            payload={"url": "https://example.com"},
            workflow_id="wf_99",
            duration_ms=45.0,
        )

        self.assertIsNotNone(msg)
        self.assertEqual(msg.event_type, "page_loaded")
        bus.publish.assert_called_once()
        published_topic, published_data = bus.publish.call_args[0]
        self.assertEqual(published_topic, "page_loaded")
        self.assertEqual(published_data["metadata"]["workflow_id"], "wf_99")


class TestBrowserEventDispatcher(unittest.TestCase):
    """Tests for core BrowserEventDispatcher."""

    def setUp(self):
        self.bus = MagicMock()
        self.dispatcher = BrowserEventDispatcher(bus=self.bus)

    def test_dispatch_and_logging(self):
        msg = self.dispatcher.dispatch(
            BrowserEventType.ARTICLE_EXTRACTED,
            payload={"title": "Quantum Computing", "words": 500},
            workflow_id="wf_test",
            session_id="s_test",
        )
        self.assertIsNotNone(msg)
        self.assertEqual(msg.event_type, "article_extracted")

        # Verify recorded in logger buffer
        logs = self.dispatcher.logger_buffer.get_events(workflow_id="wf_test")
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0].payload["title"], "Quantum Computing")

    def test_event_replay(self):
        self.dispatcher.dispatch(
            BrowserEventType.CLICK_COMPLETED,
            payload={"target": "Submit Button"},
            workflow_id="wf_replay",
        )
        self.dispatcher.dispatch(
            BrowserEventType.PAGE_LOADED,
            payload={"url": "https://example.com/home"},
            workflow_id="wf_replay",
        )

        replayed_messages = []
        count = self.dispatcher.replay_events(
            lambda msg: replayed_messages.append(msg),
            workflow_id="wf_replay",
        )
        self.assertEqual(count, 2)
        self.assertEqual(replayed_messages[0].event_type, "click_completed")
        self.assertEqual(replayed_messages[1].event_type, "page_loaded")


# ==============================================================================
# Subsystem Event Listener & Subscription Integration Tests
# ==============================================================================

class TestSubsystemListeners(unittest.TestCase):
    """Tests for Workflow, Memory, Knowledge, and Vision event listeners."""

    def test_workflow_listener(self):
        workflow_engine = MagicMock()
        listener = WorkflowEventListener(workflow_engine_ref=workflow_engine)

        evt_data = {
            "event_type": "page_loaded",
            "metadata": {"workflow_id": "wf_1"},
            "payload": {"url": "https://a.com"},
        }
        listener.on_event(evt_data)
        self.assertEqual(len(listener.processed_events), 1)
        workflow_engine.on_browser_event.assert_called_once_with(evt_data)

    def test_memory_listener(self):
        memory_engine = MagicMock()
        listener = MemoryEventListener(memory_engine_ref=memory_engine)

        evt_data = {
            "event_type": "article_extracted",
            "payload": {"text": "Article content"},
        }
        listener.on_event(evt_data)
        self.assertEqual(len(listener.memory_records), 1)
        memory_engine.store_memory.assert_called_once()

    def test_knowledge_listener(self):
        knowledge_engine = MagicMock()
        listener = KnowledgeEventListener(knowledge_engine_ref=knowledge_engine)

        evt_data = {
            "event_type": "table_extracted",
            "payload": {"headers": ["Col 1", "Col 2"], "rows": [["1", "2"]]},
        }
        listener.on_event(evt_data)
        self.assertEqual(len(listener.knowledge_records), 1)
        knowledge_engine.add_knowledge.assert_called_once()

    def test_vision_listener(self):
        vision_engine = MagicMock()
        listener = VisionEventListener(vision_engine_ref=vision_engine)

        evt_data = {
            "event_type": "screenshot_created",
            "payload": {"image_bytes": b"fake_png"},
        }
        listener.on_event(evt_data)
        self.assertEqual(len(listener.vision_records), 1)
        vision_engine.analyze_ui.assert_called_once()


# ==============================================================================
# End-to-End Workflow Integration Pipeline Test
# ==============================================================================

class TestEndToEndWorkflowEventPipeline(unittest.TestCase):
    """
    Simulates complete event-driven pipeline:
    Open URL -> PAGE_LOADED event -> Extract Article -> ARTICLE_EXTRACTED event -> Memory & Knowledge Engined updated via EventBus.
    """

    def test_full_event_driven_pipeline(self):
        # Create mock EventBus supporting subscribe & publish
        handlers = {}

        def mock_subscribe(topic, handler):
            if topic not in handlers:
                handlers[topic] = []
            handlers[topic].append(handler)

        def mock_publish(topic, data):
            if topic in handlers:
                for h in handlers[topic]:
                    h(data)

        bus = MagicMock()
        bus.subscribe.side_effect = mock_subscribe
        bus.publish.side_effect = mock_publish

        dispatcher = BrowserEventDispatcher(bus=bus)

        # Mock engine references
        workflow_engine = MagicMock()
        memory_engine = MagicMock()
        knowledge_engine = MagicMock()

        dispatcher.register_subsystems(
            workflow_engine=workflow_engine,
            memory_engine=memory_engine,
            knowledge_engine=knowledge_engine,
        )

        # 1. Dispatch PAGE_LOADED
        dispatcher.dispatch(
            BrowserEventType.PAGE_LOADED,
            payload={"url": "https://news.com/tech"},
            workflow_id="wf_pipeline",
        )

        # 2. Dispatch ARTICLE_EXTRACTED
        dispatcher.dispatch(
            BrowserEventType.ARTICLE_EXTRACTED,
            payload={"url": "https://news.com/tech", "title": "AI Breakthrough", "body": "Details..."},
            workflow_id="wf_pipeline",
        )

        # 3. Dispatch TABLE_EXTRACTED
        dispatcher.dispatch(
            BrowserEventType.TABLE_EXTRACTED,
            payload={"url": "https://news.com/tech", "headers": ["Model", "Score"]},
            workflow_id="wf_pipeline",
        )

        # Verify Workflow Engine received events
        self.assertGreaterEqual(workflow_engine.on_browser_event.call_count, 1)

        # Verify Memory Engine received ARTICLE_EXTRACTED
        memory_engine.store_memory.assert_called_once()

        # Verify Knowledge Engine received ARTICLE_EXTRACTED & TABLE_EXTRACTED
        self.assertEqual(knowledge_engine.add_knowledge.call_count, 2)


if __name__ == "__main__":
    unittest.main()
