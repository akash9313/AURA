import logging
from typing import Any, Dict, List

logger = logging.getLogger("AURA.Conversation.Context")


class ConversationContext:
    def __init__(self):
        self._turns: List[Dict[str, Any]] = []
        self._metadata: Dict[str, Any] = {}

    def add_turn(self, role: str, text: str) -> None:
        self._turns.append({"role": role, "text": text})

    def get_history(self) -> List[Dict[str, Any]]:
        return list(self._turns)

    def clear(self) -> None:
        self._turns.clear()
        self._metadata.clear()
