import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from memory.models import WorkingMemoryState

logger = logging.getLogger("AURA.Memory.WorkingMemory")


class WorkingMemory:
    """
    Manages short-term working memory for active user turns and goals.

    Automatically clears or resets after a conversation concludes.
    """

    def __init__(self, conversation_id: str = None):
        self.conversation_id = conversation_id or str(uuid.uuid4())
        self.task: Optional[str] = None
        self.goal: Optional[str] = None
        self.messages: List[Dict[str, Any]] = []
        self.temp_variables: Dict[str, Any] = {}
        self.updated_at: datetime = datetime.now()

    def start_new_session(self, conversation_id: str = None) -> str:
        """Start a fresh working memory session."""
        self.conversation_id = conversation_id or str(uuid.uuid4())
        self.clear()
        logger.info(f"Started new Working Memory session: '{self.conversation_id}'")
        return self.conversation_id

    def set_task(self, task: str) -> None:
        """Set active task in working memory."""
        self.task = task
        self.updated_at = datetime.now()

    def set_goal(self, goal: str) -> None:
        """Set active goal in working memory."""
        self.goal = goal
        self.updated_at = datetime.now()

    def add_message(self, role: str, content: str) -> None:
        """Buffer a message in working memory."""
        msg = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.messages.append(msg)
        self.updated_at = datetime.now()

    def set_variable(self, key: str, value: Any) -> None:
        """Store a temporary session variable."""
        self.temp_variables[key] = value
        self.updated_at = datetime.now()

    def get_variable(self, key: str, default: Any = None) -> Any:
        """Get a temporary session variable."""
        return self.temp_variables.get(key, default)

    def clear(self) -> None:
        """Clear all active working memory context."""
        self.task = None
        self.goal = None
        self.messages.clear()
        self.temp_variables.clear()
        self.updated_at = datetime.now()
        logger.debug(f"Cleared Working Memory for session: '{self.conversation_id}'")

    def snapshot(self) -> WorkingMemoryState:
        """Get snapshot object of current working memory state."""
        return WorkingMemoryState(
            conversation_id=self.conversation_id,
            task=self.task,
            goal=self.goal,
            messages=list(self.messages),
            temp_variables=dict(self.temp_variables),
            updated_at=self.updated_at
        )
