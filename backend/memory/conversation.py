import logging
import uuid
from datetime import datetime
from typing import List, Optional
from memory.models import ConversationMessage, ConversationRecord
from memory.store import BaseMemoryRepository

logger = logging.getLogger("AURA.Memory.Conversation")


class ConversationMemory:
    """
    Manages long-term storage and retrieval of full conversation sessions.
    """

    def __init__(self, repo: BaseMemoryRepository):
        self.repo = repo
        self.active_record: Optional[ConversationRecord] = None

    def start_conversation(self, conversation_id: str = None) -> ConversationRecord:
        """Start recording a new conversation session."""
        cid = conversation_id or str(uuid.uuid4())
        self.active_record = ConversationRecord(
            conversation_id=cid,
            title="Active Conversation",
            started_at=datetime.now()
        )
        self.repo.save_conversation(self.active_record)
        logger.info(f"Started ConversationMemory session: '{cid}'")
        return self.active_record

    def add_message(self, role: str, content: str) -> None:
        """Append a turn message to the active conversation session."""
        if not self.active_record:
            self.start_conversation()

        msg = ConversationMessage(
            role=role,
            content=content,
            timestamp=datetime.now()
        )
        self.active_record.messages.append(msg)
        self.repo.save_conversation(self.active_record)

    def finish_conversation(
        self, title: str = None, summary: str = None, keywords: List[str] = None
    ) -> Optional[ConversationRecord]:
        """Mark the active conversation as completed and save summary metadata."""
        if not self.active_record:
            return None

        self.active_record.finished_at = datetime.now()
        if title:
            self.active_record.title = title
        if summary:
            self.active_record.summary = summary
        if keywords:
            self.active_record.keywords = keywords

        self.repo.save_conversation(self.active_record)
        logger.info(f"Finished ConversationMemory session: '{self.active_record.conversation_id}'")
        record = self.active_record
        self.active_record = None
        return record

    def get_conversation(self, conversation_id: str) -> Optional[ConversationRecord]:
        """Retrieve a stored conversation by its unique ID."""
        return self.repo.get_conversation(conversation_id)

    def search_conversations(self, query: str, limit: int = 10) -> List[ConversationRecord]:
        """Search across stored conversation titles, summaries, keywords, and content."""
        return self.repo.search_conversations(query, limit=limit)

    def list_history(self, limit: int = 10) -> List[ConversationRecord]:
        """Retrieve recent conversation session records."""
        return self.repo.list_conversations(limit=limit)
