import logging
import uuid
from typing import List
from knowledge.models import DocumentChunk

logger = logging.getLogger("AURA.Knowledge.Chunker")


class TextChunker:
    """
    Splits text documents into overlapping chunk windows for vector embedding & retrieval.
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, document_id: str, content: str) -> List[DocumentChunk]:
        chunks = []
        words = content.split()

        if not words:
            return chunks

        step = max(1, self.chunk_size - self.overlap)
        index = 0

        for i in range(0, len(words), step):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = " ".join(chunk_words)
            chunk_id = f"chk_{document_id}_{index}"
            chunk = DocumentChunk(
                chunk_id=chunk_id,
                document_id=document_id,
                content=chunk_text,
                chunk_index=index,
                metadata={"word_count": len(chunk_words)}
            )
            chunks.append(chunk)
            index += 1

        logger.info(f"Chunked document '{document_id}' into {len(chunks)} chunk(s).")
        return chunks
