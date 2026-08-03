from enum import Enum


class KnowledgeEvent(Enum):
    """Event definitions for Knowledge Intelligence Platform."""
    DOCUMENT_IMPORTED = "document_imported"
    DOCUMENT_INDEXED = "document_indexed"
    KNOWLEDGE_UPDATED = "knowledge_updated"
    SEARCH_COMPLETED = "search_completed"
    SUMMARY_GENERATED = "summary_generated"
    COLLECTION_CREATED = "collection_created"
