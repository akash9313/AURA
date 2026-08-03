import logging
from typing import Dict, List, Optional
from knowledge.models import DocumentChunk, KnowledgeDocument
from knowledge.providers.base import BaseEmbeddingProvider
from knowledge.providers.local_embedding import LocalEmbeddingProvider

logger = logging.getLogger("AURA.Knowledge.Index")


class KnowledgeIndexManager:
    """
    Vector and keyword indexing store for document chunks.
    """

    def __init__(self, embedding_provider: Optional[BaseEmbeddingProvider] = None):
        self.embedding_provider = embedding_provider if embedding_provider is not None else LocalEmbeddingProvider()
        self.documents: Dict[str, KnowledgeDocument] = {}
        self.chunks: Dict[str, DocumentChunk] = {}

    def index_document(self, doc: KnowledgeDocument) -> None:
        self.documents[doc.document_id] = doc
        for chunk in doc.chunks:
            if not chunk.embedding:
                chunk.embedding = self.embedding_provider.embed_text(chunk.content)
            self.chunks[chunk.chunk_id] = chunk
        logger.info(f"Indexed document '{doc.title}' ({len(doc.chunks)} chunks).")

    def remove_document(self, document_id: str) -> None:
        doc = self.documents.pop(document_id, None)
        if doc:
            for chunk in doc.chunks:
                self.chunks.pop(chunk.chunk_id, None)
            logger.info(f"Removed document '{document_id}' from index store.")
