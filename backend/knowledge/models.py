from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import time


class SourceType(Enum):
    PDF = "pdf"
    MARKDOWN = "markdown"
    TEXT = "text"
    DOCX = "docx"
    HTML = "html"
    CSV = "csv"
    CODE = "code"
    WEB = "web"
    CONVERSATION = "conversation"


@dataclass
class DocumentChunk:
    """Atomic text chunk with embedding vector and metadata."""
    chunk_id: str
    document_id: str
    content: str
    chunk_index: int
    embedding: List[float] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeDocument:
    """Document entity in knowledge repository."""
    document_id: str
    title: str
    source_type: SourceType
    file_path: Optional[str] = None
    collection_id: str = "default"
    tags: List[str] = field(default_factory=list)
    chunks: List[DocumentChunk] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_id": self.document_id,
            "title": self.title,
            "source_type": self.source_type.value,
            "file_path": self.file_path,
            "collection_id": self.collection_id,
            "tags": self.tags,
            "chunk_count": len(self.chunks),
            "created_at": self.created_at,
        }


@dataclass
class KnowledgeCollection:
    """Organized knowledge folder/collection."""
    collection_id: str
    name: str
    description: str
    tags: List[str] = field(default_factory=list)
    is_private: bool = True
    created_at: float = field(default_factory=time.time)


@dataclass
class SearchResult:
    """Result chunk matched during search."""
    chunk: DocumentChunk
    document_title: str
    source_type: str
    score: float
    citation: str


@dataclass
class CitationInfo:
    """Source reference citation metadata."""
    source_title: str
    chunk_id: str
    excerpt: str
