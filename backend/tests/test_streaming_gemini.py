import time
import unittest
from core.events import Event
from core.event_bus import EventBus
from brain.streaming.configuration import StreamingLLMConfig
from brain.streaming.context_builder import ContextBuilder
from brain.streaming.events import StreamingLLMEvent
from brain.streaming.gemini_stream import GeminiStreamingProvider
from brain.streaming.models import StreamState
from brain.streaming.response_buffer import StreamingResponseBuffer
from brain.streaming.service import StreamingBrainService


class TestStreamingGemini(unittest.TestCase):

    def setUp(self):
        self.bus = EventBus()
        self.config = StreamingLLMConfig()
        self.context_builder = ContextBuilder(config=self.config)
        self.response_buffer = StreamingResponseBuffer()
        self.provider = GeminiStreamingProvider(config=self.config)
        self.service = StreamingBrainService(bus=self.bus, config=self.config)

    def test_context_builder(self):
        """Test prompt context assembly with history and memory."""
        self.context_builder.add_history("user", "Hello")
        self.context_builder.add_history("assistant", "Hi there!")

        context = self.context_builder.build_prompt_context("What is AURA?", memory_context="User prefers dark mode.")
        self.assertIn("System:", context)
        self.assertIn("Memory Context: User prefers dark mode.", context)
        self.assertIn("User: What is AURA?", context)

    def test_response_buffer_metrics(self):
        """Test response buffer token accumulation and first-token latency (<800ms)."""
        self.response_buffer.start_session()
        c1 = self.response_buffer.add_token("Hello")
        self.assertTrue(c1.is_first_token)

        c2 = self.response_buffer.add_token(" world")
        self.assertFalse(c2.is_first_token)

        payload = self.response_buffer.get_payload()
        self.assertEqual(payload.full_text, "Hello world")
        self.assertEqual(payload.total_tokens, 2)
        self.assertLess(payload.first_token_latency_ms, 800.0)

    def test_gemini_streaming_provider(self):
        """Test streaming provider token generator."""
        tokens = list(self.provider.generate_stream("Test prompt"))
        self.assertGreater(len(tokens), 0)
        self.assertIn("AURA", "".join(tokens))

    def test_streaming_brain_service_event_lifecycle(self):
        """Test StreamingBrainService receives TEXT_READY and emits streaming events."""
        self.service.start()
        received_events = []

        def event_listener(evt, payload):
            received_events.append((evt, payload))

        self.bus.subscribe(StreamingLLMEvent.LLM_STARTED.value, lambda p: event_listener(StreamingLLMEvent.LLM_STARTED.value, p))
        self.bus.subscribe(Event.STREAMING_RESPONSE, lambda p: event_listener(Event.STREAMING_RESPONSE, p))
        self.bus.subscribe(Event.AI_RESPONSE_READY, lambda p: event_listener(Event.AI_RESPONSE_READY, p))

        self.bus.publish(Event.TEXT_READY, "What is AURA?")
        time.sleep(0.35)  # Wait for background thread stream completion

        event_names = [evt for evt, _ in received_events]
        self.assertIn(StreamingLLMEvent.LLM_STARTED.value, event_names)
        self.assertIn(Event.STREAMING_RESPONSE, event_names)
        self.assertIn(Event.AI_RESPONSE_READY, event_names)

    def test_cancellation_support(self):
        """Test cancelling streaming LLM response."""
        self.service.start()
        cancelled_events = []
        self.bus.subscribe(StreamingLLMEvent.LLM_CANCELLED.value, lambda p: cancelled_events.append(p))

        self.bus.publish(Event.TEXT_READY, "Long query to cancel")
        time.sleep(0.02)
        self.service.cancel_stream()

        self.assertEqual(self.service.state, StreamState.CANCELLED)
        self.assertEqual(len(cancelled_events), 1)


if __name__ == "__main__":
    unittest.main()
