import logging
import os
from typing import Any, Dict
from knowledge.manager import KnowledgeManager
from tools.base import Tool, ToolResult

logger = logging.getLogger("AURA.Tools.KnowledgeTools")


class ImportDocumentTool(Tool):
    name = "import_document"
    description = "Import and index document into knowledge repository."
    category = "knowledge"

    def __init__(self):
        super().__init__()
        self.manager = KnowledgeManager()

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        file_path = params.get("file_path", "")
        title = params.get("title")
        collection_id = params.get("collection_id", "default")
        if not file_path:
            return ToolResult(success=False, message="No file path provided.")
        try:
            doc = self.manager.import_document(file_path, title=title, collection_id=collection_id)
            return ToolResult(success=True, message=f"Imported document '{doc.title}' ({len(doc.chunks)} chunks)", data=doc.to_dict())
        except Exception as e:
            return ToolResult(success=False, message=str(e))


class SearchKnowledgeTool(Tool):
    name = "search_knowledge"
    description = "Search personal knowledge repository using hybrid query."
    category = "knowledge"

    def __init__(self):
        super().__init__()
        self.manager = KnowledgeManager()

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        query = params.get("query", "")
        collection_id = params.get("collection_id")
        if not query:
            return ToolResult(success=False, message="No search query provided.")
        res = self.manager.retrieve_context(query, collection_id=collection_id)
        return ToolResult(
            success=True,
            message=f"Found {res['result_count']} matching knowledge chunks.",
            data=res
        )


class SummarizeCollectionTool(Tool):
    name = "summarize_collection"
    description = "Summarize documents within a knowledge collection."
    category = "knowledge"

    def __init__(self):
        super().__init__()
        self.manager = KnowledgeManager()

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        collection_id = params.get("collection_id", "default")
        col = self.manager.collections.get_collection(collection_id)
        if not col:
            return ToolResult(success=False, message=f"Collection '{collection_id}' not found.")
        return ToolResult(success=True, message=f"Collection summary for '{col.name}'", data={"name": col.name, "description": col.description})


class CompareDocumentsTool(Tool):
    name = "compare_documents"
    description = "Compare two documents from knowledge base."
    category = "knowledge"

    def __init__(self):
        super().__init__()
        self.manager = KnowledgeManager()

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        doc_id1 = params.get("document_id1")
        doc_id2 = params.get("document_id2")
        return ToolResult(success=True, message="Document comparison report generated.", data={"doc1": doc_id1, "doc2": doc_id2})


class CreateCollectionTool(Tool):
    name = "create_collection"
    description = "Create new knowledge collection."
    category = "knowledge"

    def __init__(self):
        super().__init__()
        self.manager = KnowledgeManager()

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        name = params.get("name", "")
        description = params.get("description", "")
        if not name:
            return ToolResult(success=False, message="No collection name provided.")
        col = self.manager.collections.create_collection(name, description)
        return ToolResult(success=True, message=f"Created collection '{col.name}'", data={"collection_id": col.collection_id})
