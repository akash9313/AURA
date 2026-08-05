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

    def start_conversation(self, wake_word: str = "hey aura") -> ConversationSession:
        sid = f"conv_{uuid.uuid4().hex[:8]}"
        self.session = ConversationSession(session_id=sid, current_state=ConversationState.IDLE)
        self.state_machine = ConversationStateMachine(self.session)
        self.context.clear()

        self._publish_event(ConversationEvent.CONVERSATION_STARTED, {"session_id": sid, "wake_word": wake_word})
        self.start_listening()
        return self.session

    def start_listening(self) -> None:
        if not self.session or not self.state_machine:
            return

        self.state_machine.transition_to(ConversationState.LISTENING)
        self._publish_event(ConversationEvent.LISTENING_STARTED, {"session_id": self.session.session_id})

    def on_transcription_completed(self, text: str) -> None:
        if not self.session or not self.state_machine:
            return

        self.context.add_turn("user", text)
        self.state_machine.transition_to(ConversationState.TRANSCRIBING)
        self._publish_event(ConversationEvent.TRANSCRIPTION_COMPLETED, {"session_id": self.session.session_id, "text": text})
        self.start_thinking(text)

    def start_thinking(self, text: str) -> None:
        if not self.session or not self.state_machine:
            return

        self.state_machine.transition_to(ConversationState.THINKING)
        self._publish_event(ConversationEvent.LLM_STARTED, {"session_id": self.session.session_id, "text": text})

    def on_llm_completed(self, response_text: str) -> None:
        if not self.session or not self.state_machine:
            return

        self.context.add_turn("assistant", response_text)
        self._publish_event(ConversationEvent.LLM_COMPLETED, {"session_id": self.session.session_id, "response": response_text})
        self.start_responding(response_text)

    def start_responding(self, response_text: str) -> None:
        if not self.session or not self.state_machine:
            return

        self.state_machine.transition_to(ConversationState.RESPONDING)
        self._publish_event(ConversationEvent.TTS_STARTED, {"session_id": self.session.session_id, "response": response_text})

    def on_tts_completed(self) -> None:
        if not self.session or not self.state_machine:
            return

        self._publish_event(ConversationEvent.TTS_COMPLETED, {"session_id": self.session.session_id})

        if self.config.enable_followup_mode:
            self.enter_followup_mode()
        else:
            self.end_conversation()

    def enter_followup_mode(self) -> None:
        if not self.session or not self.state_machine:
            return

        self.state_machine.transition_to(ConversationState.WAITING_FOR_FOLLOWUP)

        try:
            loop = asyncio.get_running_loop()
            self._followup_task = loop.create_task(self._wait_for_followup_timeout())
        except RuntimeError:
            pass

    async def _wait_for_followup_timeout(self) -> None:
        await asyncio.sleep(self.config.followup_timeout_sec)
        if self.session and self.session.current_state == ConversationState.WAITING_FOR_FOLLOWUP:
            self.end_conversation()

    def handle_user_interruption(self) -> None:
        if not self.session:
            return

        if self.session.current_state in (ConversationState.RESPONDING, ConversationState.SPEAKING):
            self.interruption_handler.handle_interruption(self.session, self.session.current_state)

            if self._followup_task and not self._followup_task.done():
                self._followup_task.cancel()

            self.start_listening()

    def end_conversation(self) -> None:
        if not self.session or not self.state_machine:
            return

        sid = self.session.session_id
        self.state_machine.transition_to(ConversationState.IDLE)
        self._publish_event(ConversationEvent.CONVERSATION_ENDED, {"session_id": sid})

    def _publish_event(self, event: ConversationEvent, data: Dict[str, Any]) -> None:
        if self.bus:
            try:
                self.bus.publish(event.value, data)
            except Exception as e:
                logger.error(f"Failed to publish conversation event '{event.value}': {e}")
