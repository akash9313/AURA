import logging
import time
from typing import Any, Dict
from tools.base import Tool
from tools.result import ToolResult
from vision.manager import VisionManager

logger = logging.getLogger("AURA.Tools.Vision.ReadDocument")


class ReadDocumentTool(Tool):
    """Tool for reading PDF files or document images."""

    def __init__(self, vision_mgr: VisionManager = None):
        self.vision_mgr = vision_mgr if vision_mgr is not None else VisionManager()

    @property
    def name(self) -> str:
        return "read_document"

    @property
    def description(self) -> str:
        return "Reads and extracts text, headings, and summaries from a document image or PDF file."

    @property
    def category(self) -> str:
        return "vision"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        doc_path = parameters.get("document_path") or parameters.get("filepath") or parameters.get("path")
        if not doc_path:
            return ToolResult(
                success=False,
                message="No document path provided.",
                execution_time=time.time() - start_time
            )

        try:
            res = self.vision_mgr.read_pdf_page(doc_path)
            elapsed = time.time() - start_time
            return ToolResult(
                success=True,
                message=f"Document summary: {res.summary}",
                data=res.to_dict(),
                execution_time=elapsed
            )
        except Exception as e:
            logger.error(f"ReadDocumentTool execution failed: {e}")
            return ToolResult(
                success=False,
                message=f"Failed to read document: {e}",
                execution_time=time.time() - start_time
            )
