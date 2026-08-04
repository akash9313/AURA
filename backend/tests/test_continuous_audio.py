import time
import unittest
from core.events import Event
from core.event_bus import EventBus
from speech.audio_stream import AudioStreamConfig, ContinuousAudioPipeline
from speech.speech_service import SpeechService


class TestContinuousAudioPipeline(unittest.TestCase):

    def setUp(self):
        self.bus = EventBus()
        self.config = AudioStreamConfig(sample_rate=16000, channels=1, frame_duration_ms=10)
        self.pipeline = ContinuousAudioPipeline(bus=self.bus, config=self.config)

    def tearDown(self):
        if self.pipeline.is_streaming:
            self.pipeline.stop()

    def test_audio_config_defaults(self):
        """Test default AudioStreamConfig values."""
        cfg = AudioStreamConfig()
        self.assertEqual(cfg.sample_rate, 16000)
        self.assertEqual(cfg.channels, 1)
        self.assertEqual(cfg.audio_format, "int16")

    def test_lifecycle_start_stop(self):
        """Test continuous audio pipeline graceful start and stop lifecycle."""
        self.assertFalse(self.pipeline.is_streaming)
        started = self.pipeline.start()
        self.assertTrue(started)
        self.assertTrue(self.pipeline.is_streaming)

        # Idempotent start call
        self.assertFalse(self.pipeline.start())

        time.sleep(0.05)
        stopped = self.pipeline.stop()
        self.assertTrue(stopped)
        self.assertFalse(self.pipeline.is_streaming)

        # Idempotent stop call
        self.assertFalse(self.pipeline.stop())

    def test_audio_chunk_event_bus_emission(self):
        """Test that EventBus receives MIC_STARTED, AUDIO_CHUNK, and MIC_STOPPED events."""
        received_events = []

        def event_listener(event, payload):
            received_events.append((event, payload))

        self.bus.subscribe(Event.MIC_STARTED, lambda p: event_listener(Event.MIC_STARTED, p))
        self.bus.subscribe(Event.AUDIO_CHUNK, lambda p: event_listener(Event.AUDIO_CHUNK, p))
        self.bus.subscribe(Event.MIC_STOPPED, lambda p: event_listener(Event.MIC_STOPPED, p))

        self.pipeline.start()
        time.sleep(0.05)
        self.pipeline.stop()

        event_names = [evt for evt, _ in received_events]
        self.assertIn(Event.MIC_STARTED, event_names)
        self.assertIn(Event.AUDIO_CHUNK, event_names)
        self.assertIn(Event.MIC_STOPPED, event_names)

        # Check payload fields of AUDIO_CHUNK
        chunk_payloads = [p for evt, p in received_events if evt == Event.AUDIO_CHUNK]
        self.assertGreater(len(chunk_payloads), 0)
        sample_chunk = chunk_payloads[0]
        self.assertIn("audio_data", sample_chunk)
        self.assertEqual(sample_chunk["sample_rate"], 16000)
        self.assertEqual(sample_chunk["channels"], 1)
        self.assertIn("timestamp", sample_chunk)
        self.assertIn("frame_index", sample_chunk)

    def test_custom_chunk_callback(self):
        """Test registering a custom callback for audio chunks."""
        chunks = []
        self.pipeline.set_chunk_callback(lambda p: chunks.append(p))

        self.pipeline.start()
        time.sleep(0.04)
        self.pipeline.stop()

        self.assertGreater(len(chunks), 0)

    def test_speech_service_integration(self):
        """Test SpeechService manages ContinuousAudioPipeline lifecycle."""
        service = SpeechService(bus=self.bus, audio_config=self.config)
        service.start()
        self.assertTrue(service.continuous_audio.is_streaming)

        time.sleep(0.03)
        service.stop()
        self.assertFalse(service.continuous_audio.is_streaming)


if __name__ == "__main__":
    unittest.main()
