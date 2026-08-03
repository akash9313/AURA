import os
import unittest
from knowledge.chunker import TextChunker
from knowledge.collections import CollectionManager
from knowledge.index import KnowledgeIndexManager
from knowledge.ingestion import IngestionPipeline
from knowledge.manager import KnowledgeManager
from knowledge.parser import DocumentParser
from knowledge.providers.local_embedding import LocalEmbeddingProvider
from knowledge.retrieval import KnowledgeRetrievalEngine
from knowledge.search import KnowledgeSearchEngine
from tools.knowledge_tools import (
    CompareDocumentsTool,
    CreateCollectionTool,
    ImportDocumentTool,
    SearchKnowledgeTool,
    SummarizeCollectionTool,
)


class TestKnowledgePlatform(unittest.TestCase):

    def test_chunker(self):
        """Test TextChunker sliding window chunking."""
        chunker = TextChunker(chunk_size=10, overlap=2)
        text = "word " * 25
        chunks = chunker.chunk_text("doc_1", text)
        self.assertGreater(len(chunks), 1)

    def test_local_embedding(self):
        """Test local feature hashing embedding provider."""
        embedder = LocalEmbeddingProvider(vector_dim=16)
        vec = embedder.embed_text("event-driven architecture")
        self.assertEqual(len(vec), 16)

    def test_ingestion_search_and_retrieval(self):
        """Test document indexing, hybrid search, and context retrieval."""
        index_mgr = KnowledgeIndexManager()
        ingestion = IngestionPipeline(index_mgr)
        search_engine = KnowledgeSearchEngine(index_mgr)
        retrieval = KnowledgeRetrievalEngine(search_engine)

        test_file = os.path.join(os.getcwd(), "README.md")
        if os.path.exists(test_file):
            doc = ingestion.ingest_file(test_file, title="AURA Readme")
            self.assertEqual(doc.title, "AURA Readme")

            context = retrieval.retrieve_context("AURA")
            self.assertGreater(context["result_count"], 0)

    def test_collection_manager(self):
        """Test KnowledgeCollection creation and retrieval."""
        cols = CollectionManager()
        col = cols.create_collection("DBMS Notes", "Database Management Systems")
        self.assertEqual(col.name, "DBMS Notes")

    def test_knowledge_tools(self):
        """Test Knowledge Platform Tool implementations."""
        create_col_tool = CreateCollectionTool()
        res_col = create_col_tool.execute({"name": "AI Research", "description": "AI papers"})
        self.assertTrue(res_col.success)

        search_tool = SearchKnowledgeTool()
        res_search = search_tool.execute({"query": "architecture"})
        self.assertTrue(res_search.success)


if __name__ == "__main__":
    unittest.main()
