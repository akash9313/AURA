"""
Master Conversation Manager Engine.
Orchestrates voice conversation lifecycle across wake word trigger, streaming STT, LLM thinking,
TTS responding, interruptions, follow-up modes, and state machine transitions.
Contains NO duplicated STT/LLM/TTS logic; coordinates existing services.
"""

import asyncio
import logging
import time
import uuid
from typing import Any, Dict, Optional

from conversation.configuration import ConversationConfig
from conversation.context import ConversationContext
from conversation.events import ConversationEvent
from conversation.interruption import InterruptionHandler
from conversation.models import ConversationSession, ConversationState
from conversation.state_machine import ConversationStateMachine
from conversation.timeout_manager import ConversationTimeoutManager

logger = logging.getLogger("AURA.Conversation.Manager")


class ConversationManager:
    """
    Master Voice Conversation Lifecycle Manager.
    """

    def __init__(
        self,
        bus: Any = None,
        config: Optional[ConversationConfig] = None,
    ):
        self.bus = bus
        self.config = config or ConversationConfig()
        self.context = ConversationContext()
        self.interruption_handler = InterruptionHandler(bus=bus)
        self.timeout_manager = ConversationTimeoutManager(self.config)

        self.session: Optional[ConversationSession] = None
        self.state_machine: Optional[ConversationStateMachine] = None
        self._followup_task: Optional[asyncio.Task] = None

        logger.info("ConversationManager initialized")

    def start_conversation(self, wake_word: str = "hey aura") -> ConversationSession:
        """
        Start new conversation session upon wake word trigger.
        """
        sid = f"conv_{uuid.uuid4().hex[:8]}"
        self.session = ConversationSession(session_id=sid, current_state=ConversationState.IDLE)
        self.state_machine = ConversationStateMachine(self.session)
        self.context.clear()

        logger.info(f"Starting conversation session '{sid}' (Wake word: '{wake_word}')...")
        self._publish_event(ConversationEvent.CONVERSATION_STARTED, {"session_id": sid, "wake_word": wake_word})

        # Transition to LISTENING
        self.start_listening()
        return self.session

    def start_listening(self) -> None:
        """Transition session to LISTENING."""
        if not self.session or not self.state_machine:
            return

        self.state_machine.transition_to(ConversationState.LISTENING)
        self._publish_event(ConversationEvent.LISTENING_STARTED, {"session_id": self.session.session_id})

    def on_transcription_completed(self, text: str) -> None:
        """
        Handle completed STT transcript.
        """
        if not self.session or not self.state_machine:
            return

        logger.info(f"STT Transcript received: '{text}'")
        self.context.add_turn("user", text)
        self.state_machine.transition_to(ConversationState.TRANSCRIBING)
        self._publish_event(ConversationEvent.TRANSCRIPTION_COMPLETED, {"session_id": self.session.session_id, "text": text})

        # Transition to THINKING for LLM processing
        self.start_thinking(text)

    def start_thinking(self, text: str) -> None:
        """Transition session to THINKING."""
        if not self.session or not self.state_machine:
            return

        self.state_machine.transition_to(ConversationState.THINKING)
        self._publish_event(ConversationEvent.LLM_STARTED, {"session_id": self.session.session_id, "text": text})

    def on_llm_completed(self, response_text: str) -> None:
        """
        Handle completed LLM response text.
        """
        if not self.session or not self.state_machine:
            return

        logger.info(f"LLM Response ready: '{response_text[:40]}...'")
        self.context.add_turn("assistant", response_text)
        self._publish_event(ConversationEvent.LLM_COMPLETED, {"session_id": self.session.session_id, "response": response_text})

        # Transition to RESPONDING for TTS playback
        self.start_responding(response_text)

    def start_responding(self, response_text: str) -> None:
        """Transition session to RESPONDING / SPEAKING."""
        if not self.session or not self.state_machine:
            return

        self.state_machine.transition_to(ConversationState.RESPONDING)
        self._publish_event(ConversationEvent.TTS_STARTED, {"session_id": self.session.session_id, "response": response_text})

    def on_tts_completed(self) -> None:
        """
        Handle completed TTS voice playback -> enter follow-up mode.
        """
        if not self.session or not self.state_machine:
            return

        self._publish_event(ConversationEvent.TTS_COMPLETED, {"session_id": self.session.session_id})

        if self.config.enable_followup_mode:
            self.enter_followup_mode()
        else:
            self.end_conversation()

    def enter_followup_mode(self) -> None:
        """
        Keep conversation active for followup_timeout_sec waiting for follow-up speech.
        """
        if not self.session or not self.state_machine:
            return

        self.state_machine.transition_to(ConversationState.WAITING_FOR_FOLLOWUP)
        logger.info(f"Entering follow-up mode for {self.config.followup_timeout_sec}s...")

        try:
            loop = asyncio.get_running_loop()
            self._followup_task = loop.create_task(self._wait_for_followup_timeout())
        except RuntimeError:
            pass

    async def _wait_for_followup_timeout(self) -> None:
        """Wait for follow-up timeout to elapse, returning to IDLE if no follow-up utterance arrives."""
        await asyncio.sleep(self.config.followup_timeout_sec)
        if self.session and self.session.current_state == ConversationState.WAITING_FOR_FOLLOWUP:
            logger.info("Follow-up timeout elapsed. Returning conversation to IDLE.")
            self.end_conversation()

    def handle_user_interruption(self) -> None:
        """
        Handle user speech interruption while TTS is active.
        """
        if not self.session:
            return

        if self.session.current_state in (ConversationState.RESPONDING, ConversationState.SPEAKING):
            self.interruption_handler.handle_interruption(self.session, self.session.current_state)

            if self._followup_task and not self._followup_task.done():
                self._followup_task.cancel()

            # Return immediately to LISTENING
            self.start_listening()

    def end_conversation(self) -> None:
        """
        End conversation session and transition back to IDLE.
        """
        if not self.session or not self.state_machine:
            return

        sid = self.session.session_id
        self.state_machine.transition_to(ConversationState.IDLE)
        self._publish_event(ConversationEvent.CONVERSATION_ENDED, {"session_id": sid})
        logger.info(f"Conversation session '{sid}' ended cleanly")

    def _publish_event(self, event: ConversationEvent, data: Dict[str, Any]) -> None:
        if self.bus:
            try:
                self.bus.publish(event.value, data)
            except Exception as e:
                logger.error(f"Failed to publish conversation event '{event.value}': {e}")
