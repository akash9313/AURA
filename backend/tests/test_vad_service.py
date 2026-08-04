import array
import math
import time
import unittest
from core.events import Event
from core.event_bus import EventBus
from speech.audio_stream import AudioStreamConfig, ContinuousAudioPipeline
from speech.vad.configuration import VADConfig
from speech.vad.detector import VoiceActivityDetector
from speech.vad.events import VADEvent
from speech.vad.models import VADState
from speech.vad.service import VADService


class TestVADService(unittest.TestCase):

    def setUp(self):
        self.bus = EventBus()
        self.config = VADConfig(
            energy_threshold=100.0,
            min_speech_duration_ms=20.0,
            min_silence_duration_ms=40.0
        )
        self.detector = VoiceActivityDetector(config=self.config)
        self.service = VADService(bus=self.bus, config=self.config)

    def generate_pcm_sine(self, duration_ms: float = 20.0, amplitude: int = 5000) -> bytes:
        """Helper to generate synthetic PCM 16-bit audio frames."""
        num_samples = int(16000 * (duration_ms / 1000.0))
        samples = array.array("h")
        for i in range(num_samples):
            val = int(amplitude * math.sin(2 * math.pi * 440 * (i / 16000.0)))
            samples.append(val)
        return samples.tobytes()

    def generate_pcm_silence(self, duration_ms: float = 20.0) -> bytes:
        """Helper to generate silent PCM 16-bit audio frames."""
        num_samples = int(16000 * (duration_ms / 1000.0))
        return b"\x00" * (num_samples * 2)

    def test_rms_energy_calculation(self):
        """Test RMS energy computation on silent vs high-amplitude PCM audio."""
        silence = self.generate_pcm_silence(20.0)
        speech = self.generate_pcm_sine(20.0, amplitude=5000)

        silence_energy = self.detector.compute_rms_energy(silence)
        speech_energy = self.detector.compute_rms_energy(speech)

        self.assertEqual(silence_energy, 0.0)
        self.assertGreater(speech_energy, 1000.0)

    def test_state_machine_transitions(self):
        """Test state machine transitions: IDLE -> LISTENING -> SPEAKING -> SILENCE."""
        silence = self.generate_pcm_silence(20.0)
        speech = self.generate_pcm_sine(20.0, amplitude=5000)

        # 1. Initial silence frame
        state, seg = self.detector.analyze_frame(silence)
        self.assertEqual(state, VADState.LISTENING)
        self.assertFalse(seg.is_speech)

        # 2. Speech frames (duration >= min_speech_duration_ms)
        self.detector.analyze_frame(speech)
        time.sleep(0.025)
        state2, seg2 = self.detector.analyze_frame(speech)

        self.assertEqual(state2, VADState.SPEAKING)
        self.assertTrue(seg2.is_speech)

        # 3. Silence frames following speech (duration >= min_silence_duration_ms)
        self.detector.analyze_frame(silence)
        time.sleep(0.045)
        state3, seg3 = self.detector.analyze_frame(silence)

        self.assertEqual(state3, VADState.SILENCE)
        self.assertFalse(seg3.is_speech)

    def test_vad_service_event_bus_integration(self):
        """Test VADService processes AUDIO_CHUNK events and emits VADEvents onto EventBus."""
        self.service.start()
        received_events = []

        def event_listener(event, payload):
            received_events.append((event, payload))

        self.bus.subscribe(VADEvent.VOICE_STARTED.value, lambda p: event_listener(VADEvent.VOICE_STARTED.value, p))
        self.bus.subscribe(VADEvent.VOICE_CONTINUING.value, lambda p: event_listener(VADEvent.VOICE_CONTINUING.value, p))
        self.bus.subscribe(VADEvent.VOICE_ENDED.value, lambda p: event_listener(VADEvent.VOICE_ENDED.value, p))

        speech_chunk = self.generate_pcm_sine(20.0, amplitude=5000)
        silence_chunk = self.generate_pcm_silence(20.0)

        # Publish speech chunk 1 & 2
        self.bus.publish(Event.AUDIO_CHUNK, {"audio_data": speech_chunk})
        time.sleep(0.025)
        self.bus.publish(Event.AUDIO_CHUNK, {"audio_data": speech_chunk})

        # Publish silence chunk 1 & 2
        self.bus.publish(Event.AUDIO_CHUNK, {"audio_data": silence_chunk})
        time.sleep(0.045)
        self.bus.publish(Event.AUDIO_CHUNK, {"audio_data": silence_chunk})

        event_names = [evt for evt, _ in received_events]
        self.assertIn(VADEvent.VOICE_STARTED.value, event_names)
        self.assertIn(VADEvent.VOICE_ENDED.value, event_names)

    def test_corrupted_frame_resilience(self):
        """Test detector resilience to empty or corrupted bytes."""
        state, seg = self.detector.analyze_frame(b"")
        self.assertEqual(seg.energy, 0.0)

        state2, seg2 = self.detector.analyze_frame(b"\x01")
        self.assertEqual(seg2.energy, 0.0)

    def test_end_to_end_continuous_audio_stream_with_vad(self):
        """Integration test linking ContinuousAudioPipeline -> VADService -> EventBus."""
        self.service.start()

        pipeline_config = AudioStreamConfig(sample_rate=16000, channels=1, frame_duration_ms=10)
        pipeline = ContinuousAudioPipeline(bus=self.bus, config=pipeline_config)

        events = []
        self.bus.subscribe(Event.AUDIO_CHUNK, lambda p: events.append("AUDIO_CHUNK"))
        self.bus.subscribe(VADEvent.SILENCE_DETECTED.value, lambda p: events.append("SILENCE_DETECTED"))

        pipeline.start()
        time.sleep(0.05)
        pipeline.stop()

        self.assertIn("AUDIO_CHUNK", events)
        self.assertIn("SILENCE_DETECTED", events)


if __name__ == "__main__":
    unittest.main()
