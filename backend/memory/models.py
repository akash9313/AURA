from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class WorkingMemoryState:
    """Represents transient state for the current active conversation."""
    conversation_id: str
    task: Optional[str] = None
    goal: Optional[str] = None
    messages: List[Dict[str, Any]] = field(default_factory=list)
    temp_variables: Dict[str, Any] = field(default_factory=dict)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "conversation_id": self.conversation_id,
            "task": self.task,
            "goal": self.goal,
            "messages": self.messages,
            "temp_variables": self.temp_variables,
            "updated_at": self.updated_at.isoformat()
        }


@dataclass
class ConversationMessage:
    """Represents a single utterance or turn in a conversation."""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class ConversationRecord:
    """Represents a completed or archived conversation session."""
    conversation_id: str
    title: str = "Untitled Conversation"
    summary: str = ""
    keywords: List[str] = field(default_factory=list)
    messages: List[ConversationMessage] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    finished_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "conversation_id": self.conversation_id,
            "title": self.title,
            "summary": self.summary,
            "keywords": self.keywords,
            "messages": [msg.to_dict() for msg in self.messages],
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat() if self.finished_at else None
        }


@dataclass
class ProfileFact:
    """Represents a long-term user preference or fact."""
    key: str
    value: str
    category: str = "preference"  # 'preference', 'identity', 'skill', 'rule'
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "value": self.value,
            "category": self.category,
            "updated_at": self.updated_at.isoformat()
        }


@dataclass
class KnowledgeDocument:
    """Represents an ingested knowledge item or document."""
    doc_id: str
    title: str
    content: str
    doc_type: str = "text"  # 'pdf', 'markdown', 'text', 'web', 'code'
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "title": self.title,
            "content": self.content,
            "doc_type": self.doc_type,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class MemoryQuery:
    """Parameters for querying memories."""
    query_text: str
    memory_type: str = "all"  # 'working', 'conversation', 'profile', 'knowledge', 'all'
    limit: int = 10


@dataclass
class MemorySearchResult:
    """Standardized search match returned across memory systems."""
    memory_type: str
    item_id: str
    title: str
    content: str
    score: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
