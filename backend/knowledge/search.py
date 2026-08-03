import logging
from typing import List, Optional
from knowledge.index import KnowledgeIndexManager
from knowledge.models import SearchResult

logger = logging.getLogger("AURA.Knowledge.Search")


class KnowledgeSearchEngine:
    """
    Hybrid search engine combining vector similarity and keyword matching.
    """

    def __init__(self, index_manager: KnowledgeIndexManager):
        self.index_manager = index_manager

    def search(self, query: str, collection_id: Optional[str] = None, top_k: int = 5) -> List[SearchResult]:
        query_vec = self.index_manager.embedding_provider.embed_text(query)
        results = []

        for chunk_id, chunk in self.index_manager.chunks.items():
            doc = self.index_manager.documents.get(chunk.document_id)
            if not doc:
                continue

            if collection_id and doc.collection_id != collection_id:
                continue

            # Cosine similarity calculation
            score = 0.0
            if chunk.embedding and query_vec:
                score = sum(a * b for a, b in zip(chunk.embedding, query_vec))

            # Keyword bonus
            if query.lower() in chunk.content.lower():
                score += 0.2

            citation = f"[{doc.title} - Chunk {chunk.chunk_index}]"
            results.append(SearchResult(
                chunk=chunk,
                document_title=doc.title,
                source_type=doc.source_type.value,
                score=round(score, 4),
                citation=citation
            ))

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]
