import logging
from typing import Any, Dict, List, Optional
from knowledge.citations import CitationFormatter
from knowledge.collections import CollectionManager
from knowledge.index import KnowledgeIndexManager
from knowledge.ingestion import IngestionPipeline
from knowledge.models import KnowledgeDocument, SearchResult
from knowledge.permissions import KnowledgePermissionValidator
from knowledge.retrieval import KnowledgeRetrievalEngine
from knowledge.search import KnowledgeSearchEngine
from knowledge.summarizer import KnowledgeSummarizer

logger = logging.getLogger("AURA.Knowledge.Manager")


class KnowledgeManager:
    """
    Master Knowledge Intelligence Platform Orchestrator.
    """

    def __init__(self):
        self.index_manager = KnowledgeIndexManager()
        self.ingestion = IngestionPipeline(self.index_manager)
        self.search_engine = KnowledgeSearchEngine(self.index_manager)
        self.retrieval_engine = KnowledgeRetrievalEngine(self.search_engine)
        self.summarizer = KnowledgeSummarizer()
        self.citations = CitationFormatter()
        self.collections = CollectionManager()
        self.permissions = KnowledgePermissionValidator()

    def import_document(self, file_path: str, title: Optional[str] = None, collection_id: str = "default") -> KnowledgeDocument:
        return self.ingestion.ingest_file(file_path, title=title, collection_id=collection_id)

    def search_knowledge(self, query: str, collection_id: Optional[str] = None, top_k: int = 5) -> List[SearchResult]:
        return self.search_engine.search(query, collection_id=collection_id, top_k=top_k)

    def retrieve_context(self, query: str, collection_id: Optional[str] = None, top_k: int = 3) -> Dict[str, Any]:
        return self.retrieval_engine.retrieve_context(query, collection_id=collection_id, top_k=top_k)
