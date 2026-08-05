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

    def start(self) -> None:
        if self._running:
            return

        self._running = True
        self.state = WakeWordEngineState.LISTENING

        if not self.provider.initialize():
            self.state = WakeWordEngineState.ERROR
            self._publish_event(WakeWordEvent.WAKEWORD_ERROR, {"error": "Provider init failed"})
            return

        self._publish_event(WakeWordEvent.WAKEWORD_LISTENING, {"provider": self.provider.get_provider_name()})

        try:
            loop = asyncio.get_running_loop()
            self._listen_task = loop.create_task(self._continuous_listen_loop())
        except RuntimeError:
            pass

    def stop(self) -> None:
        self._running = False
        self.state = WakeWordEngineState.STOPPED

        if self._listen_task and not self._listen_task.done():
            self._listen_task.cancel()

        if self.provider:
            self.provider.shutdown()

    def is_healthy(self) -> bool:
        return self.state != WakeWordEngineState.ERROR

    async def _continuous_listen_loop(self) -> None:
        while self._running:
            try:
                pcm_chunk = self.audio_buffer.read_all()

                if pcm_chunk:
                    now = time.time()
                    if now - self._last_detection_time >= self.config.cooldown_sec:
                        res = self.provider.process_frame(pcm_chunk)

                        if res.detected:
                            self._last_detection_time = now
                            self.state = WakeWordEngineState.DETECTED
                            self._publish_event(WakeWordEvent.WAKEWORD_DETECTED, res.to_dict())
                            self.state = WakeWordEngineState.LISTENING

                await asyncio.sleep(0.05)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Wake Word listening loop error: {e}")
                self.state = WakeWordEngineState.ERROR
                self._publish_event(WakeWordEvent.WAKEWORD_ERROR, {"error": str(e)})

                if self.config.auto_restart_on_error and self._running:
                    await asyncio.sleep(1.0)
                    self.state = WakeWordEngineState.LISTENING

    def push_audio_chunk(self, pcm_chunk: bytes) -> None:
        self.audio_buffer.write(pcm_chunk)

    def _publish_event(self, event: WakeWordEvent, data: Dict[str, Any]) -> None:
        if self.bus:
            try:
                self.bus.publish(event.value, data)
            except Exception as e:
                logger.error(f"Failed to publish wake word event '{event.value}': {e}")
