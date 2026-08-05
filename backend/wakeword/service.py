"""
Always-Listening Wake Word Engine Service.
Top-level AURA service managing continuous microphone monitoring, wake word detection,
EventBus publishing, low CPU concurrency, and automatic failure recovery.
"""

import asyncio
import logging
import sys
import time
from typing import Any, Dict, Optional

from core.service import Service
from wakeword.audio_buffer import AudioRingBuffer
from wakeword.configuration import WakeWordConfig
from wakeword.events import WakeWordEvent
from wakeword.models import WakeWordDetectionResult, WakeWordEngineState
from wakeword.openwakeword_provider import OpenWakeWordProvider
from wakeword.provider import BaseWakeWordProvider

logger = logging.getLogger("AURA.WakeWord.Service")


class WakeWordService(Service):
    """
    Always-listening Wake Word Engine Service.
    """

    def __init__(
        self,
        bus: Any = None,
        config: Optional[WakeWordConfig] = None,
        provider: Optional[BaseWakeWordProvider] = None,
    ):
        super().__init__(bus)
        self.config = config or WakeWordConfig()
        self.provider = provider or OpenWakeWordProvider(self.config)
        self.audio_buffer = AudioRingBuffer()

        self.state = WakeWordEngineState.STOPPED
        self._running = False
        self._listen_task: Optional[asyncio.Task] = None
        self._last_detection_time = 0.0

        logger.info("WakeWordService initialized")

    # ------------------------------------------------------------------
    # Service Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start Wake Word Engine listening loop."""
        if self._running:
            logger.warning("WakeWordService is already running")
            return

        logger.info("Starting WakeWordService...")
        self._running = True
        self.state = WakeWordEngineState.LISTENING

        # Initialize provider
        if not self.provider.initialize():
            logger.error("Failed to initialize Wake Word provider")
            self.state = WakeWordEngineState.ERROR
            self._publish_event(WakeWordEvent.WAKEWORD_ERROR, {"error": "Provider init failed"})
            return

        self._publish_event(WakeWordEvent.WAKEWORD_LISTENING, {"provider": self.provider.get_provider_name()})

        # Launch async continuous listening loop
        try:
            loop = asyncio.get_running_loop()
            self._listen_task = loop.create_task(self._continuous_listen_loop())
        except RuntimeError:
            # If no running loop, create task when loop becomes available
            pass

        logger.info("WakeWordService started successfully")

    def stop(self) -> None:
        """Gracefully stop Wake Word Engine listening loop."""
        logger.info("Stopping WakeWordService...")
        self._running = False
        self.state = WakeWordEngineState.STOPPED

        if self._listen_task and not self._listen_task.done():
            self._listen_task.cancel()

        if self.provider:
            self.provider.shutdown()

        logger.info("WakeWordService stopped")

    def is_healthy(self) -> bool:
        return self.state != WakeWordEngineState.ERROR

    # ------------------------------------------------------------------
    # Continuous Listening Loop
    # ------------------------------------------------------------------

    async def _continuous_listen_loop(self) -> None:
        """Continuous background listening loop with automatic failure recovery."""
        logger.info("Continuous wake word monitoring active...")

        while self._running:
            try:
                # Read accumulated PCM chunk from audio buffer
                pcm_chunk = self.audio_buffer.read_all()

                if pcm_chunk:
                    # Enforce detection cooldown
                    now = time.time()
                    if now - self._last_detection_time >= self.config.cooldown_sec:
                        res = self.provider.process_frame(pcm_chunk)

                        if res.detected:
                            self._last_detection_time = now
                            self.state = WakeWordEngineState.DETECTED
                            logger.info(f"Wake word detected: '{res.wake_word}' (confidence: {res.confidence})")
                            self._publish_event(WakeWordEvent.WAKEWORD_DETECTED, res.to_dict())

                            # Return to listening after handling trigger
                            self.state = WakeWordEngineState.LISTENING

                # Low CPU usage sleep interval
                await asyncio.sleep(0.05)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Wake Word listening loop error: {e}")
                self.state = WakeWordEngineState.ERROR
                self._publish_event(WakeWordEvent.WAKEWORD_ERROR, {"error": str(e)})

                if self.config.auto_restart_on_error and self._running:
                    logger.info("Attempting automatic restart of Wake Word loop...")
                    await asyncio.sleep(1.0)
                    self.state = WakeWordEngineState.LISTENING

    def push_audio_chunk(self, pcm_chunk: bytes) -> None:
        """Push microphone PCM audio chunk into ring buffer."""
        self.audio_buffer.write(pcm_chunk)

    def _publish_event(self, event: WakeWordEvent, data: Dict[str, Any]) -> None:
        if self.bus:
            try:
                self.bus.publish(event.value, data)
            except Exception as e:
                logger.error(f"Failed to publish wake word event '{event.value}': {e}")
