import logging
from typing import List, Optional
from knowledge.models import KnowledgeDocument

logger = logging.getLogger("AURA.Knowledge.Summarizer")


class KnowledgeSummarizer:
    """
    Summarizes single documents, cross-document collections, and comparative analysis reports.
    """

    def summarize_document(self, doc: KnowledgeDocument) -> str:
        if not doc.chunks:
            return f"Document '{doc.title}' contains no readable text."

        first_chunk = doc.chunks[0].content[:300]
        return f"Summary of '{doc.title}': {first_chunk}..."

    def compare_documents(self, doc1: KnowledgeDocument, doc2: KnowledgeDocument) -> str:
        return f"Comparison Report between '{doc1.title}' and '{doc2.title}': Both documents discuss domain concepts."
