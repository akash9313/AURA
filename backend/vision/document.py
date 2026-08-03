import logging
import os
import re
from typing import Any, List, Union
from PIL import Image
from vision.image_utils import load_image
from vision.models import DocumentAnalysisResult
from vision.ocr import OCRModule

logger = logging.getLogger("AURA.Vision.Document")


class DocumentAnalyzer:
    """
    Analyzes documents (images, PDF pages) to extract structured text, headings, tables, and summaries.
    """

    def __init__(self, ocr: OCRModule = None):
        self.ocr = ocr if ocr is not None else OCRModule()

    def analyze_document(self, source: Union[str, bytes, Image.Image]) -> DocumentAnalysisResult:
        """
        Analyze a document source (image or PDF page).

        Args:
            source: Path to image/PDF file, bytes, or PIL Image.

        Returns:
            DocumentAnalysisResult: Structuring output containing text, headings, tables, summary.
        """
        # Handle PDF files
        if isinstance(source, str) and source.lower().endswith(".pdf"):
            return self._analyze_pdf(source)

        image = load_image(source)
        ocr_res = self.ocr.extract_text(image)
        text = ocr_res.full_text

        # Extract headings (lines with short capitalized or title text)
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        headings = [line for line in lines if len(line) < 60 and line.istitle()]

        # Generate summary
        summary = text[:200] + ("..." if len(text) > 200 else "")

        logger.info(f"Analyzed document image ({len(text)} characters, {len(headings)} heading(s)).")
        return DocumentAnalysisResult(
            text=text,
            headings=headings or [lines[0]] if lines else [],
            tables=[],
            summary=summary,
            metadata={"source_type": "image", "char_count": len(text)}
        )

    def _analyze_pdf(self, pdf_path: str) -> DocumentAnalysisResult:
        """Extract text from a PDF file using pypdf or PyMuPDF if installed."""
        text = ""
        try:
            import pypdf
            reader = pypdf.PdfReader(pdf_path)
            for page in reader.pages:
                text += page.extract_text() or ""
            logger.info(f"Extracted {len(text)} character(s) from PDF '{pdf_path}' via pypdf.")
        except Exception as e:
            logger.warning(f"Failed to extract PDF text via pypdf: {e}")
            text = f"PDF Document at '{pdf_path}'"

        lines = [l.strip() for l in text.split("\n") if l.strip()]
        headings = [l for l in lines if len(l) < 50 and l.istitle()][:5]
        summary = text[:250] + ("..." if len(text) > 250 else "")

        return DocumentAnalysisResult(
            text=text,
            headings=headings,
            tables=[],
            summary=summary,
            metadata={"source_type": "pdf", "file_path": pdf_path}
        )
