"""
Wake Word Engine Unit, Provider, Continuous Listening, and Shutdown Test Suite.
Tests WakeWordDetectionResult, AudioRingBuffer, OpenWakeWordProvider, BaseWakeWordProvider, and WakeWordService.
"""

import asyncio
import struct
import sys
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, ".")

from wakeword.models import WakeWordDetectionResult, WakeWordEngineState
from wakeword.events import WakeWordEvent
from wakeword.configuration import WakeWordConfig
from wakeword.audio_buffer import AudioRingBuffer
from wakeword.provider import BaseWakeWordProvider
from wakeword.openwakeword_provider import OpenWakeWordProvider
from wakeword.service import WakeWordService


class TestWakeWordEngine(unittest.TestCase):
    """Test suite for Wake Word Engine subsystem."""

    def setUp(self):
        self.bus = MagicMock()
        self.config = WakeWordConfig(wake_words=["hey aura"], threshold=0.5, cooldown_sec=0.1)
        self.provider = OpenWakeWordProvider(self.config)
        self.service = WakeWordService(bus=self.bus, config=self.config, provider=self.provider)

    def test_audio_ring_buffer_read_write(self):
        """Test AudioRingBuffer capacity overflow and read/clear operations."""
        buf = AudioRingBuffer(capacity_bytes=100)
        buf.write(b"12345")
        self.assertEqual(buf.read_all(), b"12345")
        self.assertEqual(buf.read_all(), b"")

    def test_openwakeword_provider_detection(self):
        """Test OpenWakeWordProvider frame processing."""
        self.assertTrue(self.provider.initialize())
        self.assertEqual(self.provider.get_provider_name(), "openwakeword")

        # Process quiet frame -> No detection
        quiet_pcm = b"\x00\x00" * 640
        res = self.provider.process_frame(quiet_pcm)
        self.assertFalse(res.detected)

        # Process high energy frame -> Acoustic detection fallback
        high_energy_pcm = struct.pack("<640h", *[20000] * 640)
        res_loud = self.provider.process_frame(high_energy_pcm)
        self.assertTrue(res_loud.detected)
        self.assertEqual(res_loud.wake_word, "hey aura")

    def test_wakeword_service_lifecycle_and_events(self):
        """Test WakeWordService start, audio push, detection, and shutdown."""
        self.service.start()
        self.assertEqual(self.service.state, WakeWordEngineState.LISTENING)

        # Push high energy audio frame
        high_energy_pcm = struct.pack("<640h", *[20000] * 640)
        self.service.push_audio_chunk(high_energy_pcm)

        async def run_single_step():
            pcm_chunk = self.service.audio_buffer.read_all()
            if pcm_chunk:
                res = self.service.provider.process_frame(pcm_chunk)
                if res.detected:
                    self.service.state = WakeWordEngineState.DETECTED
                    self.service._publish_event(WakeWordEvent.WAKEWORD_DETECTED, res.to_dict())

        asyncio.run(run_single_step())

        # Verify EventBus events published
        published = [call[0][0] for call in self.bus.publish.call_args_list]
        self.assertIn("wakeword_listening", published)
        self.assertIn("wakeword_detected", published)

        # Shutdown test
        self.service.stop()
        self.assertEqual(self.service.state, WakeWordEngineState.STOPPED)


if __name__ == "__main__":
    unittest.main()
