import logging
from typing import Any, Dict, List, Optional
from memory.conversation import ConversationMemory
from memory.models import (
    ConversationRecord,
    KnowledgeDocument,
    MemorySearchResult,
    ProfileFact,
)
from memory.profile import ProfileMemory
from memory.store import BaseMemoryRepository, SQLiteMemoryRepository
from memory.summarizer import MemorySummarizer
from memory.working_memory import WorkingMemory

logger = logging.getLogger("AURA.Memory.Manager")


class MemoryManager:
    """
    Central Entry Point for the AURA Memory Engine.

    Coordinates Working Memory, Conversation Memory, Profile Memory, and Knowledge Memory systems.
    """

    def __init__(self, repo: BaseMemoryRepository = None):
        """
        Initialize MemoryManager.

        Args:
            repo (BaseMemoryRepository, optional): Repository storage implementation. Defaults to SQLiteMemoryRepository.
        """
        self.repo = repo if repo is not None else SQLiteMemoryRepository()
        self.working = WorkingMemory()
        self.conversation = ConversationMemory(self.repo)
        self.profile_mem = ProfileMemory(self.repo)
        self.summarizer = MemorySummarizer()
        logger.info("MemoryManager initialized.")

    # --- Profile API ---
    def remember(self, key: str, value: str, category: str = "preference") -> ProfileFact:
        """Explicitly store a user fact or preference."""
        return self.profile_mem.save_fact(key, value, category=category)

    def recall(self, key: str) -> Optional[str]:
        """Recall a user fact or preference by key."""
        return self.profile_mem.get_fact(key)

    def forget(self, key: str) -> bool:
        """Forget an explicit user fact or preference."""
        return self.profile_mem.delete_fact(key)

    def profile(self) -> Dict[str, str]:
        """Get all stored long-term user facts and preferences."""
        return self.profile_mem.list_facts()

    # --- Conversation API ---
    def history(self, limit: int = 10) -> List[ConversationRecord]:
        """Retrieve recent conversation session records."""
        return self.conversation.list_history(limit=limit)

    def summarize(self, conversation_id: str = None) -> Optional[ConversationRecord]:
        """Summarize and save a conversation session."""
        cid = conversation_id or self.conversation.active_record.conversation_id if self.conversation.active_record else None
        if not cid:
            return None

        record = self.conversation.get_conversation(cid)
        if not record:
            return None

        summary_data = self.summarizer.summarize_conversation(record)
        return self.conversation.finish_conversation(
            title=summary_data["title"],
            summary=summary_data["summary"],
            keywords=summary_data["keywords"]
        )

    # --- Unified Search API ---
    def search(self, query_text: str, limit: int = 10) -> List[MemorySearchResult]:
        """
        Search across profile facts, stored conversations, and knowledge documents.
        """
        results: List[MemorySearchResult] = []
        q = query_text.lower().strip()

        # 1. Search Profile Facts
        for k, v in self.profile_mem.list_facts().items():
            if q in k.lower() or q in v.lower():
                results.append(MemorySearchResult(
                    memory_type="profile",
                    item_id=k,
                    title=f"User Fact: {k}",
                    content=v,
                    score=1.0
                ))

        # 2. Search Conversations
        convs = self.conversation.search_conversations(query_text, limit=limit)
        for c in convs:
            results.append(MemorySearchResult(
                memory_type="conversation",
                item_id=c.conversation_id,
                title=c.title,
                content=f"{c.summary} | Messages: {len(c.messages)}",
                score=0.9,
                metadata={"keywords": c.keywords}
            ))

        # 3. Search Knowledge Docs
        docs = self.repo.search_knowledge_docs(query_text, limit=limit)
        for d in docs:
            results.append(MemorySearchResult(
                memory_type="knowledge",
                item_id=d.doc_id,
                title=d.title,
                content=d.content[:200],
                score=0.8,
                metadata=d.metadata
            ))

        return results[:limit]

    # --- Advanced Utility API ---
    def merge(self, key: str, value: str) -> ProfileFact:
        """Merge/update a memory key-value pair."""
        return self.profile_mem.update_fact(key, value)

    def export(self) -> Dict[str, Any]:
        """Export full snapshot of profile and conversation history."""
        return {
            "profile": self.profile_mem.list_facts(),
            "history": [c.to_dict() for c in self.conversation.list_history(limit=50)],
            "working": self.working.snapshot().to_dict()
        }
