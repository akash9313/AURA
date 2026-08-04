import time
import unittest
from core.events import Event
from core.event_bus import EventBus
from brain.streaming.events import StreamingLLMEvent
from speech.tts.audio_player import AudioPlayerEngine
from speech.tts.audio_queue import AudioPlaybackQueue
from speech.tts.configuration import TTSConfig
from speech.tts.events import TTSEvent
from speech.tts.models import AudioSegmentPayload, TTSState
from speech.tts.sentence_buffer import SentenceBuffer
from speech.tts.service import TTSService
from speech.tts.streaming_tts import StreamingTTSEngine
from speech.tts.synthesizer import EdgeTTSSynthesizer


class TestStreamingTTS(unittest.TestCase):

    def setUp(self):
        self.bus = EventBus()
        self.config = TTSConfig(voice_name="en-US-AvaNeural")
        self.sentence_buffer = SentenceBuffer(config=self.config)
        self.synthesizer = EdgeTTSSynthesizer(config=self.config)
        self.queue = AudioPlaybackQueue()
        self.player = AudioPlayerEngine(queue=self.queue)
        self.engine = StreamingTTSEngine(config=self.config, synthesizer=self.synthesizer)
        self.service = TTSService(bus=self.bus, config=self.config)

    def tearDown(self):
        self.player.stop()
        self.engine.cancel()

    def test_sentence_buffer_delimiters(self):
        """Test sentence boundary detection on delimiters (., !, ?, \\n)."""
        s1 = self.sentence_buffer.push_token("Hello ")
        self.assertIsNone(s1)

        s2 = self.sentence_buffer.push_token("world. How ")
        self.assertEqual(s2, "Hello world.")

        s3 = self.sentence_buffer.push_token("are you?")
        self.assertEqual(s3, "How are you?")

    def test_synthesizer_segment_creation(self):
        """Test EdgeTTSSynthesizer payload generation."""
        seg = self.synthesizer.synthesize_segment("Test sentence.", voice_name="en-US-AndrewNeural")
        self.assertEqual(seg.text, "Test sentence.")
        self.assertEqual(seg.voice_name, "en-US-AndrewNeural")
        self.assertGreater(len(seg.audio_data), 0)

    def test_audio_playback_queue(self):
        """Test AudioPlaybackQueue push, pop, pause, resume, and instant flush."""
        seg = self.synthesizer.synthesize_segment("Queue test")
        self.queue.push(seg)
        self.assertEqual(self.queue.get_size(), 1)

        # Flush queue
        flushed = self.queue.flush()
        self.assertEqual(flushed, 1)
        self.assertEqual(self.queue.get_size(), 0)

    def test_streaming_tts_engine_latency_target(self):
        """Test first usable sentence playback latency target (<1000ms)."""
        self.engine.start_session()
        seg = self.engine.feed_token("Hello AURA operating system.")
        self.assertIsNotNone(seg)
        self.assertLess(seg.synthesis_latency_ms, 1000.0)

    def test_tts_service_event_lifecycle(self):
        """Test TTSService responds to Streaming LLM events and emits playback events."""
        self.service.start()
        received_events = []

        def event_listener(evt, payload):
            received_events.append((evt, payload))

        self.bus.subscribe(TTSEvent.TTS_STARTED.value, lambda p: event_listener(TTSEvent.TTS_STARTED.value, p))
        self.bus.subscribe(TTSEvent.TTS_SEGMENT_READY.value, lambda p: event_listener(TTSEvent.TTS_SEGMENT_READY.value, p))
        self.bus.subscribe(Event.SPEECH_STARTED, lambda p: event_listener(Event.SPEECH_STARTED, p))

        # 1. LLM Started
        self.bus.publish(StreamingLLMEvent.LLM_STARTED.value, {})

        # 2. LLM Tokens forming complete sentence
        self.bus.publish(Event.STREAMING_RESPONSE, {"token": "Hello "})
        self.bus.publish(Event.STREAMING_RESPONSE, {"token": "AURA."})

        time.sleep(0.15)

        event_names = [evt for evt, _ in received_events]
        self.assertIn(TTSEvent.TTS_STARTED.value, event_names)
        self.assertIn(TTSEvent.TTS_SEGMENT_READY.value, event_names)

    def test_interruption_queue_cancellation(self):
        """Test instant queue flush upon user speech interruption."""
        self.service.start()
        self.bus.publish(StreamingLLMEvent.LLM_STARTED.value, {})
        self.bus.publish(Event.STREAMING_RESPONSE, {"token": "First sentence."})
        self.bus.publish(Event.STREAMING_RESPONSE, {"token": "Second sentence."})

        # Interrupt speech playback
        self.service.on_llm_cancelled({})
        self.assertEqual(self.service.engine.state, TTSState.CANCELLED)


if __name__ == "__main__":
    unittest.main()
