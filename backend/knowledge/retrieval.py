import logging
from typing import Any, Dict, List, Optional
from knowledge.models import SearchResult
from knowledge.search import KnowledgeSearchEngine

logger = logging.getLogger("AURA.Knowledge.Retrieval")


class KnowledgeRetrievalEngine:
    """
    Retrieval engine constructing structured context, metadata, and confidence scores for RAG workflows.
    """

    def __init__(self, search_engine: KnowledgeSearchEngine):
        self.search_engine = search_engine

    def retrieve_context(self, query: str, collection_id: Optional[str] = None, top_k: int = 3) -> Dict[str, Any]:
        results: List[SearchResult] = self.search_engine.search(query, collection_id=collection_id, top_k=top_k)

        context_chunks = [r.chunk.content for r in results]
        citations = [r.citation for r in results]
        sources = list(set([r.document_title for r in results]))

        avg_score = sum(r.score for r in results) / float(len(results)) if results else 0.0

        return {
            "query": query,
            "context": "\n---\n".join(context_chunks),
            "sources": sources,
            "citations": citations,
            "confidence_score": round(avg_score, 2),
            "result_count": len(results)
        }
