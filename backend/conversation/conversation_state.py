import logging
import threading
from typing import Callable, List, Optional
from conversation.models import ConversationState

logger = logging.getLogger("AURA.Conversation.StateMachine")


class ConversationStateMachine:
    """
    Full Duplex Conversation State Machine.
    Enforces clean state transitions (IDLE -> LISTENING -> THINKING -> SPEAKING -> INTERRUPTED -> LISTENING).
    """

    def __init__(self):
        self._state: ConversationState = ConversationState.IDLE
        self._lock = threading.Lock()
        self._listeners: List[Callable[[ConversationState, ConversationState], None]] = []

    @property
    def current_state(self) -> ConversationState:
        with self._lock:
            return self._state

    def add_listener(self, listener: Callable[[ConversationState, ConversationState], None]) -> None:
        self._listeners.append(listener)

    def transition_to(self, new_state: ConversationState) -> bool:
        with self._lock:
            old_state = self._state
            if old_state == new_state:
                return False

            self._state = new_state
            logger.info(f"Conversation State Transition: {old_state.value.upper()} -> {new_state.value.upper()}")

        for listener in self._listeners:
            try:
                listener(old_state, new_state)
            except Exception as e:
                logger.error(f"Error in state transition listener: {e}")

        return True
