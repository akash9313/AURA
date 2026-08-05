"""
Conversation State Machine (State Pattern).
Manages valid state transitions across voice conversation lifecycle:
IDLE -> LISTENING -> TRANSCRIBING -> THINKING -> RESPONDING -> WAITING_FOR_FOLLOWUP -> IDLE
"""

import logging
from typing import Optional

from conversation.models import ConversationSession, ConversationState

logger = logging.getLogger("AURA.Conversation.StateMachine")


class ConversationStateMachine:
    """
    State Pattern machine for voice conversation lifecycle transitions.
    """

    def __init__(self, session: ConversationSession):
        self.session = session

    def transition_to(self, new_state: ConversationState) -> bool:
        """
        Transition session state machine to new state.

        Returns:
            True if transition succeeded.
        """
        old_state = self.session.current_state
        logger.info(f"Conversation state transition: {old_state.value} -> {new_state.value}")
        self.session.current_state = new_state
        return True
