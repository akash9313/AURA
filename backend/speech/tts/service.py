import logging
from typing import Optional
from core.events import Event
from core.service import Service
from brain.streaming.events import StreamingLLMEvent
from speech.tts.configuration import TTSConfig
from speech.tts.events import TTSEvent
from speech.tts.models import AudioSegmentPayload, TTSState
from speech.tts.streaming_tts import StreamingTTSEngine

logger = logging.getLogger("AURA.Speech.TTS.Service")


class TTSService(Service):
    """
    Streaming Text-to-Speech (TTS) Service.
    Consumes LLM token streams, synthesizes sentence chunks incrementally, and plays audio via playback queue.
    Interruption-ready for instant cancellation.
    """

    def __init__(self, bus, config: Optional[TTSConfig] = None):
        super().__init__(bus)
        self.config = config or TTSConfig()
        self.engine = StreamingTTSEngine(
            config=self.config,
            on_segment_ready=self.on_segment_ready
        )
        self.engine.player.set_callbacks(
            on_start=self.on_audio_play_started,
            on_finish=self.on_audio_play_finished
        )

    def start(self):
        logger.info("Streaming TTS Service Started.")
        if self.bus:
            # Subscribe to Streaming LLM and Interruption Events
            self.bus.subscribe(StreamingLLMEvent.LLM_STARTED.value, self.on_llm_started)
            self.bus.subscribe(StreamingLLMEvent.LLM_PARTIAL_TOKEN.value, self.on_llm_token)
            self.bus.subscribe(Event.STREAMING_RESPONSE, self.on_llm_token)
            self.bus.subscribe(StreamingLLMEvent.LLM_FINISHED.value, self.on_llm_finished)
            self.bus.subscribe(StreamingLLMEvent.LLM_CANCELLED.value, self.on_llm_cancelled)
            self.bus.subscribe(Event.SPEECH_INTERRUPTED, self.on_llm_cancelled)

    def stop(self):
        logger.info("Streaming TTS Service Stopped.")
        self.engine.cancel()

    def on_llm_started(self, payload: dict):
        logger.info("TTS Session Started.")
        self.engine.start_session()
        if self.bus:
            self.bus.publish(TTSEvent.TTS_STARTED.value, payload)

    def on_llm_token(self, payload: dict):
        if not payload or not isinstance(payload, dict):
            return

        token = payload.get("token", "")
        if token:
            self.engine.feed_token(token)

    def on_llm_finished(self, payload: dict):
        logger.info("TTS Session Finalizing.")
        self.engine.finish_session()

    def on_llm_cancelled(self, payload: dict):
        logger.info("TTS Session Cancelled.")
        flushed_count = self.engine.cancel()
        if self.bus:
            self.bus.publish(TTSEvent.TTS_CANCELLED.value, {"flushed_segments": flushed_count})

    def on_segment_ready(self, segment: AudioSegmentPayload):
        if self.bus:
            self.bus.publish(TTSEvent.TTS_SEGMENT_READY.value, segment.to_dict())

    def on_audio_play_started(self, segment: AudioSegmentPayload):
        if self.bus:
            self.bus.publish(TTSEvent.AUDIO_PLAY_STARTED.value, segment.to_dict())
            self.bus.publish(Event.SPEECH_STARTED, segment.to_dict())

    def on_audio_play_finished(self, segment: AudioSegmentPayload):
        if self.bus:
            self.bus.publish(TTSEvent.AUDIO_PLAY_FINISHED.value, segment.to_dict())
            self.bus.publish(Event.SPEECH_COMPLETED, segment.to_dict())
