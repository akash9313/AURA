import logging
from typing import Optional

from conversation.models import ConversationSession, ConversationState

logger = logging.getLogger("AURA.Conversation.StateMachine")


class ConversationStateMachine:
    def __init__(self, session: ConversationSession):
        self.session = session

    def transition_to(self, new_state: ConversationState) -> bool:
        self.session.current_state = new_state
        return True
