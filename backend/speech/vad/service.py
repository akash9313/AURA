import logging
import time
from typing import Optional
from core.events import Event
from core.service import Service
from speech.vad.configuration import VADConfig
from speech.vad.detector import VoiceActivityDetector
from speech.vad.events import VADEvent
from speech.vad.models import VADState

logger = logging.getLogger("AURA.Speech.VAD.Service")


class VADService(Service):
    """
    Voice Activity Detection (VAD) Service.
    Subscribes to Event.AUDIO_CHUNK from Continuous Audio Pipeline and publishes VAD events to EventBus.
    """

    def __init__(self, bus, config: Optional[VADConfig] = None):
        super().__init__(bus)
        self.config = config or VADConfig()
        self.detector = VoiceActivityDetector(config=self.config)
        self.previous_state: VADState = VADState.IDLE

    def start(self):
        logger.info("VAD Service Started.")
        if self.bus:
            self.bus.subscribe(Event.AUDIO_CHUNK, self.on_audio_chunk)

    def stop(self):
        logger.info("VAD Service Stopped.")

    def on_audio_chunk(self, payload: dict):
        if not payload or "audio_data" not in payload:
            logger.warning("VAD Service received malformed audio chunk payload.")
            return

        pcm_bytes = payload["audio_data"]
        current_state, segment = self.detector.analyze_frame(pcm_bytes)

        if not self.bus:
            return

        payload_meta = {
            "timestamp": segment.timestamp,
            "energy": segment.energy,
            "confidence": segment.confidence,
            "duration": segment.duration_seconds,
            "state": current_state.value
        }

        # Transition handling & event emission
        if current_state == VADState.SPEAKING and self.previous_state != VADState.SPEAKING:
            logger.info("VAD Event -> VOICE_STARTED")
            self.bus.publish(VADEvent.VOICE_STARTED.value, payload_meta)
            self.bus.publish(Event.VOICE_STARTED, payload_meta)

        elif current_state == VADState.SPEAKING and self.previous_state == VADState.SPEAKING:
            self.bus.publish(VADEvent.VOICE_CONTINUING.value, payload_meta)

        elif current_state == VADState.SILENCE and self.previous_state == VADState.SPEAKING:
            logger.info("VAD Event -> VOICE_ENDED")
            self.bus.publish(VADEvent.VOICE_ENDED.value, payload_meta)
            self.bus.publish(Event.VOICE_ENDED, payload_meta)

        elif not segment.is_speech:
            self.bus.publish(VADEvent.SILENCE_DETECTED.value, payload_meta)

        self.previous_state = current_state

