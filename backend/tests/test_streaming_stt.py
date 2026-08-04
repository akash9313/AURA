import time
import unittest
from core.events import Event
from core.event_bus import EventBus
from speech.audio_stream import AudioStreamConfig, ContinuousAudioPipeline
from speech.stt.buffer import AudioBufferManager
from speech.stt.configuration import STTConfig
from speech.stt.events import STTEvent
from speech.stt.models import STTState
from speech.stt.segmenter import UtteranceSegmenter
from speech.stt.service import STTService
from speech.stt.streaming_whisper import StreamingWhisperEngine
from speech.stt.transcript import TranscriptFormatter
from speech.vad.configuration import VADConfig
from speech.vad.events import VADEvent
from speech.vad.service import VADService


class TestStreamingSTT(unittest.TestCase):

    def setUp(self):
        self.bus = EventBus()
        self.config = STTConfig()
        self.buffer_mgr = AudioBufferManager()
        self.segmenter = UtteranceSegmenter(config=self.config)
        self.formatter = TranscriptFormatter()
        self.engine = StreamingWhisperEngine(config=self.config, buffer_mgr=self.buffer_mgr)
        self.service = STTService(bus=self.bus, config=self.config)

    def test_audio_buffer_manager(self):
        """Test AudioBufferManager push, size, and clear operations."""
        self.assertEqual(self.buffer_mgr.get_size(), 0)
        self.buffer_mgr.push_chunk(b"\x00\x01\x02\x03")
        self.assertEqual(self.buffer_mgr.get_size(), 4)
        self.assertEqual(self.buffer_mgr.get_pcm_bytes(), b"\x00\x01\x02\x03")
        self.buffer_mgr.clear()
        self.assertEqual(self.buffer_mgr.get_size(), 0)

    def test_utterance_segmenter(self):
        """Test utterance segmentation boundary rules."""
        self.segmenter.start_utterance()
        self.assertTrue(self.segmenter.should_finalize(is_vad_ended=True))
        self.assertFalse(self.segmenter.should_finalize(is_vad_ended=False))

    def test_transcript_formatter(self):
        """Test Partial and Final transcript formatting."""
        partial = self.formatter.format_partial("  hello aura  ", duration=1.2)
        self.assertEqual(partial.text, "hello aura")
        self.assertFalse(partial.to_dict()["is_final"])

        final = self.formatter.format_final("  research AI  ", duration=2.5, inference_time_ms=120.0)
        self.assertEqual(final.text, "research AI")
        self.assertTrue(final.to_dict()["is_final"])

    def test_streaming_whisper_engine_latency(self):
        """Test partial (<300ms) and final (<700ms) inference latency targets."""
        self.buffer_mgr.push_chunk(b"\x01\x02" * 5000)

        t0 = time.time()
        partial = self.engine.transcribe_partial(duration_seconds=1.5)
        dt_partial = (time.time() - t0) * 1000.0
        self.assertLess(dt_partial, 300.0)
        self.assertTrue(partial.text)

        t0 = time.time()
        final = self.engine.transcribe_final(duration_seconds=2.0)
        dt_final = (time.time() - t0) * 1000.0
        self.assertLess(dt_final, 700.0)
        self.assertTrue(final.text)

    def test_stt_service_event_lifecycle(self):
        """Test STTService receives VAD & Audio events and publishes Transcripts."""
        self.service.start()
        received_events = []

        def event_listener(evt, payload):
            received_events.append((evt, payload))

        self.bus.subscribe(STTEvent.TRANSCRIPTION_STARTED.value, lambda p: event_listener(STTEvent.TRANSCRIPTION_STARTED.value, p))
        self.bus.subscribe(Event.PARTIAL_TRANSCRIPT, lambda p: event_listener(Event.PARTIAL_TRANSCRIPT, p))
        self.bus.subscribe(Event.FINAL_TRANSCRIPT, lambda p: event_listener(Event.FINAL_TRANSCRIPT, p))
        self.bus.subscribe(Event.TEXT_READY, lambda p: event_listener(Event.TEXT_READY, p))

        # 1. Voice Started
        self.bus.publish(VADEvent.VOICE_STARTED.value, {})
        self.assertEqual(self.service.state, STTState.BUFFERING)

        # 2. Audio Chunks
        self.bus.publish(Event.AUDIO_CHUNK, {"audio_data": b"\x01\x02" * 500})
        self.assertEqual(self.service.state, STTState.TRANSCRIBING)

        # 3. Voice Ended
        self.bus.publish(VADEvent.VOICE_ENDED.value, {})
        self.assertEqual(self.service.state, STTState.IDLE)

        event_names = [evt for evt, _ in received_events]
        self.assertIn(STTEvent.TRANSCRIPTION_STARTED.value, event_names)
        self.assertIn(Event.PARTIAL_TRANSCRIPT, event_names)
        self.assertIn(Event.FINAL_TRANSCRIPT, event_names)
        self.assertIn(Event.TEXT_READY, event_names)

    def test_full_pipeline_integration(self):
        """Integration test: ContinuousAudioPipeline -> VADService -> STTService -> EventBus."""
        vad_config = VADConfig(energy_threshold=100.0, min_speech_duration_ms=10.0, min_silence_duration_ms=20.0)
        vad_service = VADService(bus=self.bus, config=vad_config)

        vad_service.start()
        self.service.start()

        pipeline_config = AudioStreamConfig(sample_rate=16000, channels=1, frame_duration_ms=10)
        pipeline = ContinuousAudioPipeline(bus=self.bus, config=pipeline_config)

        transcripts = []
        self.bus.subscribe(Event.PARTIAL_TRANSCRIPT, lambda p: transcripts.append(p["text"]))

        pipeline.start()
        time.sleep(0.04)
        pipeline.stop()

        # Shutdown services
        vad_service.stop()
        self.service.stop()


if __name__ == "__main__":
    unittest.main()
