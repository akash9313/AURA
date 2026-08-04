import logging
from typing import Optional
from core.events import Event
from core.service import Service
from brain.streaming.events import StreamingLLMEvent
from conversation.coordinator import ConversationCoordinator
from conversation.events import ConversationEvent
from speech.tts.events import TTSEvent
from speech.vad.events import VADEvent

logger = logging.getLogger("AURA.Conversation.Service")


class ConversationService(Service):
    """
    Full Duplex Conversation & Speech Interruption Service.
    Coordinates VAD, STT, Streaming LLM, Streaming TTS, Audio Focus, and instant interruption recovery.
    """

    def __init__(self, bus):
        super().__init__(bus)
        self.coordinator = ConversationCoordinator(bus=bus)

    def start(self):
        logger.info("Full Duplex Conversation Service Started.")
        if self.bus:
            # Subscribe to pipeline events
            self.bus.subscribe(VADEvent.VOICE_STARTED.value, self.on_voice_started)
            self.bus.subscribe(Event.VOICE_STARTED, self.on_voice_started)
            self.bus.subscribe(Event.TEXT_READY, self.on_text_ready)
            self.bus.subscribe(Event.FINAL_TRANSCRIPT, self.on_text_ready)
            self.bus.subscribe(StreamingLLMEvent.LLM_PARTIAL_TOKEN.value, self.on_llm_token)
            self.bus.subscribe(Event.STREAMING_RESPONSE, self.on_llm_token)
            self.bus.subscribe(TTSEvent.AUDIO_PLAY_FINISHED.value, self.on_speech_completed)
            self.bus.subscribe(Event.SPEECH_COMPLETED, self.on_speech_completed)

    def stop(self):
        logger.info("Full Duplex Conversation Service Stopped.")

    def on_voice_started(self, payload: dict):
        self.coordinator.handle_voice_started(payload)

    def on_text_ready(self, payload: dict):
        text = payload if isinstance(payload, str) else payload.get("text", "")
        if text:
            self.coordinator.handle_text_ready(text)

    def on_llm_token(self, payload: dict):
        self.coordinator.handle_llm_token(payload)

    def on_speech_completed(self, payload: dict):
        self.coordinator.handle_speech_completed(payload)
