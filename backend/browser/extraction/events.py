"""
DOM Intelligence & Content Extraction Event Definitions.
Published to the AURA EventBus when content, articles, tables, forms, or media are extracted.
"""

from enum import Enum


class ExtractionEvent(Enum):
    """Event definitions for DOM Intelligence and Content Extraction."""
    CONTENT_EXTRACTED = "content_extracted"
    ARTICLE_FOUND = "article_found"
    TABLE_FOUND = "table_found"
    FORM_FOUND = "form_found"
    MEDIA_FOUND = "media_found"
    EXTRACTION_FAILED = "extraction_failed"
