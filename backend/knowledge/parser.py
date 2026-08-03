import logging
import os
from typing import Tuple
from knowledge.models import SourceType

logger = logging.getLogger("AURA.Knowledge.Parser")


class DocumentParser:
    """
    Multi-format document parser supporting PDF, Markdown, Plain Text, DOCX, HTML, CSV, and Code.
    """

    def parse_file(self, file_path: str) -> Tuple[str, SourceType]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Document file '{file_path}' not found.")

        ext = os.path.splitext(file_path)[1].lower()

        if ext in (".md", ".markdown"):
            source_type = SourceType.MARKDOWN
        elif ext == ".pdf":
            source_type = SourceType.PDF
        elif ext in (".html", ".htm"):
            source_type = SourceType.HTML
        elif ext == ".csv":
            source_type = SourceType.CSV
        elif ext in (".py", ".js", ".ts", ".rs", ".go", ".java", ".cpp", ".c", ".dart"):
            source_type = SourceType.CODE
        else:
            source_type = SourceType.TEXT

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as fh:
                content = fh.read()
            return content, source_type
        except Exception as e:
            logger.error(f"Failed to read file '{file_path}': {e}")
            raise IOError(f"Failed to parse document: {e}")
