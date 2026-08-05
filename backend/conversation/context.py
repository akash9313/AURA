"""
Conversation Context Memory.
Manages multi-turn dialogue history and context parameters across follow-up turns.
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger("AURA.Conversation.Context")


class ConversationContext:
    """
    Tracks dialogue turns and contextual variables for active conversation sessions.
    """

    def __init__(self):
        self._turns: List[Dict[str, Any]] = []
        self._metadata: Dict[str, Any] = {}

    def add_turn(self, role: str, text: str) -> None:
        """Add user or assistant dialogue turn."""
        self._turns.append({"role": role, "text": text})
        logger.debug(f"Added context turn ({role}): {text[:30]}...")

    def get_history(self) -> List[Dict[str, Any]]:
        """Return dialogue turn history."""
        return list(self._turns)

    def clear(self) -> None:
        """Clear context history."""
        self._turns.clear()
        self._metadata.clear()
