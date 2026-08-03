import asyncio
import os
import unittest
from unittest.mock import MagicMock

from core.events import Event
from speech.streaming.audio_pipeline import StreamingAudioPipeline
from speech.streaming.audio_player import AudioPlayer
from speech.streaming.interruption import InterruptionMonitor
from speech.streaming.latency import LatencyMonitor
from speech.streaming.microphone import StreamingMicrophone
from speech.streaming.models import AudioFrame, SpeechState, VADSegment
from speech.streaming.streaming_stt import StreamingSTT
from speech.streaming.vad import VoiceActivityDetector


class TestStreamingVoice(unittest.TestCase):

    def test_vad_speech_start_and_end(self):
        """Test VAD energy threshold detection for speech start and silence end."""
        vad = VoiceActivityDetector(energy_threshold=100.0, silence_threshold_ms=100.0)

        # Silent frame
        silent_data = b"\x00\x00" * 320
        f_silent = AudioFrame(data=silent_data, timestamp=1.0)
        seg1 = vad.process_frame(f_silent)
        self.assertFalse(seg1.is_speech)

        # Loud frame (speech start)
        loud_data = b"\x50\x50" * 320
        f_loud = AudioFrame(data=loud_data, timestamp=1.05)
        seg2 = vad.process_frame(f_loud)
        self.assertTrue(seg2.is_speech)

    def test_audio_player_flush_on_interruption(self):
        """Test AudioPlayer instant flush when user interrupts speech."""
        player = AudioPlayer()
        asyncio.run(player.play_chunk(b"PCM_CHUNK_1"))
        asyncio.run(player.play_chunk(b"PCM_CHUNK_2"))
        self.assertFalse(player.queue.empty())

        # Flush queue
        player.flush()
        self.assertTrue(player.queue.empty())

    def test_interruption_monitor(self):
        """Test InterruptionMonitor triggers player flush when user speaks during SpeechState.SPEAKING."""
        player = AudioPlayer()
        asyncio.run(player.play_chunk(b"PCM_CHUNK_1"))

        interrupted = False
        def on_interrupt():
            nonlocal interrupted
            interrupted = True

        monitor = InterruptionMonitor(player=player, on_interrupt=on_interrupt)
        vad_speech = VADSegment(is_speech=True, energy_level=500.0)

        res = monitor.check_interruption(vad_speech, SpeechState.SPEAKING)
        self.assertTrue(res)
        self.assertTrue(interrupted)
        self.assertTrue(player.queue.empty())

    def test_latency_monitor(self):
        """Test LatencyMonitor telemetry tracking."""
        latency = LatencyMonitor()
        latency.start_turn()
        latency.record_stt(85.0)
        latency.record_llm_first_token(320.0)
        latency.record_tts(150.0)
        metrics = latency.finalize_turn()

        self.assertEqual(metrics.stt_latency_ms, 85.0)
        self.assertEqual(metrics.llm_latency_ms, 320.0)
        self.assertEqual(metrics.tts_latency_ms, 150.0)
        self.assertGreater(metrics.total_roundtrip_ms, 0.0)

    def test_streaming_stt_partial(self):
        """Test StreamingSTT partial transcript callback."""
        stt = StreamingSTT()
        partials = []
        frame = AudioFrame(data=b"\x10\x10" * 2000, timestamp=1.0)
        stt.feed_frame(frame, on_partial=lambda pt: partials.append(pt.text))

        final = stt.finalize()
        self.assertTrue(final.is_final)


if __name__ == "__main__":
    unittest.main()
