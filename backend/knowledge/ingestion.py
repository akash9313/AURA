import logging
import uuid
from typing import Optional
from knowledge.chunker import TextChunker
from knowledge.index import KnowledgeIndexManager
from knowledge.models import KnowledgeDocument, SourceType
from knowledge.parser import DocumentParser

logger = logging.getLogger("AURA.Knowledge.Ingestion")


class IngestionPipeline:
    """
    Ingestion pipeline: Import -> Parse -> Clean -> Chunk -> Metadata -> Index -> Store.
    """

    def __init__(self, index_manager: KnowledgeIndexManager):
        self.index_manager = index_manager
        self.parser = DocumentParser()
        self.chunker = TextChunker()

    def ingest_file(self, file_path: str, title: Optional[str] = None, collection_id: str = "default") -> KnowledgeDocument:
        content, source_type = self.parser.parse_file(file_path)
        doc_id = f"doc_{uuid.uuid4().hex[:8]}"
        doc_title = title or file_path.split("/")[-1].split("\\")[-1]

        doc = KnowledgeDocument(
            document_id=doc_id,
            title=doc_title,
            source_type=source_type,
            file_path=file_path,
            collection_id=collection_id
        )

        chunks = self.chunker.chunk_text(doc_id, content)
        doc.chunks = chunks

        self.index_manager.index_document(doc)
        logger.info(f"Successfully ingested file '{doc_title}' (ID: {doc_id}) into collection '{collection_id}'.")
        return doc
