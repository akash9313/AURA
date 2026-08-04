import logging
import time
import uuid
from typing import Optional
from conversation.audio_focus import AudioFocusManager
from conversation.cancellation import CancellationManager
from conversation.conversation_state import ConversationStateMachine
from conversation.events import ConversationEvent
from conversation.interruption import InterruptionDetector
from conversation.models import ConversationSession, ConversationState, InterruptionPayload

logger = logging.getLogger("AURA.Conversation.Coordinator")


class ConversationCoordinator:
    """
    Master Full Duplex Conversation Coordinator.
    Orchestrates turn-taking state machine, interruption detection (<150ms latency), sub-100ms cancellation,
    and feedback-free audio focus management.
    """

    def __init__(self, bus):
        self.bus = bus
        self.state_machine = ConversationStateMachine()
        self.audio_focus = AudioFocusManager()
        self.cancellation_mgr = CancellationManager(bus=bus)
        self.interruption_detector = InterruptionDetector(on_interruption_fn=self.handle_interruption)
        self.session = ConversationSession(session_id=f"conv_{uuid.uuid4().hex[:8]}")

    def handle_voice_started(self, payload: Optional[dict] = None) -> None:
        """Called when VAD detects voice activity."""
        current = self.state_machine.current_state

        if current in (ConversationState.THINKING, ConversationState.SPEAKING):
            # Interruption triggered!
            self.interruption_detector.evaluate_voice_activity(current, self.session.session_id)
        else:
            self.state_machine.transition_to(ConversationState.LISTENING)

    def handle_interruption(self, payload: InterruptionPayload) -> None:
        """Executes sub-150ms interruption workflow."""
        t0 = time.time()
        logger.info(f"USER INTERRUPTED during '{payload.interrupted_state.value.upper()}'!")

        # 1. State machine -> INTERRUPTED
        self.state_machine.transition_to(ConversationState.INTERRUPTED)
        self.session.interruption_count += 1

        # 2. Cancel LLM, TTS, Audio Queue
        cancel_res = self.cancellation_mgr.execute_cancellation(reason="user_interrupted")

        # 3. Restore microphone audio focus
        self.audio_focus.restore_mic_focus()

        # 4. State machine -> LISTENING for new user query
        self.state_machine.transition_to(ConversationState.LISTENING)

        total_latency_ms = (time.time() - t0) * 1000.0
        logger.info(f"Interruption workflow completed in {total_latency_ms:.2f}ms (Target: <150ms)")

        if self.bus:
            self.bus.publish(ConversationEvent.USER_INTERRUPTED.value, payload.to_dict())
            self.bus.publish(ConversationEvent.CONVERSATION_RESUMED.value, {"session_id": self.session.session_id})

    def handle_text_ready(self, prompt: str) -> None:
        """Called when STT completes final transcript and user reasoning begins."""
        self.state_machine.transition_to(ConversationState.THINKING)

    def handle_llm_token(self, token_payload: dict) -> None:
        """Called when streaming LLM tokens begin arriving."""
        if self.state_machine.current_state == ConversationState.THINKING:
            self.state_machine.transition_to(ConversationState.SPEAKING)
            self.audio_focus.acquire_speaker_focus()

    def handle_speech_completed(self, payload: Optional[dict] = None) -> None:
        """Called when TTS playback finishes."""
        if self.state_machine.current_state == ConversationState.SPEAKING:
            self.audio_focus.release_speaker_focus()
            self.state_machine.transition_to(ConversationState.IDLE)
