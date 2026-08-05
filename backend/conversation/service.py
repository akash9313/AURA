"""
Conversation Manager Service.
Top-level AURA service integrating ConversationManager into kernel framework.
Subscribes to EventBus for wake word triggers, STT transcripts, LLM responses, TTS completion, and interruptions.
"""

import logging
from typing import Any, Optional

from core.service import Service
from conversation.configuration import ConversationConfig
from conversation.conversation_manager import ConversationManager
from conversation.events import ConversationEvent
from conversation.models import ConversationSession, ConversationState

logger = logging.getLogger("AURA.Conversation.Service")


class ConversationService(Service):
    """
    Service wrapper connecting ConversationManager to AURA EventBus.
    """

    def __init__(
        self,
        bus: Any = None,
        config: Optional[ConversationConfig] = None,
    ):
        super().__init__(bus)
        self.config = config or ConversationConfig()
        self.manager = ConversationManager(bus=bus, config=self.config)
        logger.info("ConversationService initialized")

    def start(self) -> None:
        """Start ConversationService and subscribe to EventBus events."""
        logger.info("Starting ConversationService...")

        if self.bus:
            # Subscribe to EventBus channels
            self.bus.subscribe("wakeword_detected", self._on_wakeword_detected)
            self.bus.subscribe("final_transcript", self._on_stt_transcript)
            self.bus.subscribe("ai_response_ready", self._on_llm_response)
            self.bus.subscribe("speech_completed", self._on_tts_completed)
            self.bus.subscribe("speech_interrupted", self._on_user_interrupted)

    def stop(self) -> None:
        """Stop ConversationService."""
        logger.info("Stopping ConversationService...")
        if self.manager:
            self.manager.end_conversation()

    def is_healthy(self) -> bool:
        return True

    # ------------------------------------------------------------------
    # EventBus Handlers
    # ------------------------------------------------------------------

    def _on_wakeword_detected(self, payload: Any) -> None:
        ww = payload.get("wake_word", "hey aura") if isinstance(payload, dict) else "hey aura"
        self.manager.start_conversation(wake_word=ww)

    def _on_stt_transcript(self, payload: Any) -> None:
        text = payload.get("text", "") if isinstance(payload, dict) else str(payload)
        if text:
            self.manager.on_transcription_completed(text)

    def _on_llm_response(self, payload: Any) -> None:
        resp = payload.get("text", "") if isinstance(payload, dict) else str(payload)
        if resp:
            self.manager.on_llm_completed(resp)

    def _on_tts_completed(self, payload: Any) -> None:
        self.manager.on_tts_completed()

    def _on_user_interrupted(self, payload: Any) -> None:
        self.manager.handle_user_interruption()
