"""
AURA DOM Intelligence & Content Extraction Engine.
Converts raw web pages into structured, AI-friendly semantic models.
"""

from browser.extraction.accessibility import AccessibilityExtractor
from browser.extraction.content_extractor import ContentExtractor
from browser.extraction.dom_parser import DOMNode, DOMParser
from browser.extraction.events import ExtractionEvent
from browser.extraction.forms import FormExtractor
from browser.extraction.headings import HeadingsExtractor
from browser.extraction.links import LinkExtractor
from browser.extraction.media import MediaExtractor
from browser.extraction.metadata import MetadataExtractor
from browser.extraction.models import (
    AccessibilityInfo,
    ArticleContent,
    ExtractedButton,
    ExtractedForm,
    ExtractedImage,
    ExtractedLink,
    ExtractedTable,
    ExtractedVideo,
    FieldType,
    HeadingItem,
    LinkType,
    PageMetadata,
    ReadingStats,
    StructuredPageContent,
    TableCell,
)
from browser.extraction.readability import ReadabilityExtractor
from browser.extraction.service import DOMExtractionService
from browser.extraction.tables import TableExtractor

__all__ = [
    "DOMExtractionService",
    "ContentExtractor",
    "DOMParser",
    "DOMNode",
    "MetadataExtractor",
    "ReadabilityExtractor",
    "HeadingsExtractor",
    "LinkExtractor",
    "MediaExtractor",
    "TableExtractor",
    "FormExtractor",
    "AccessibilityExtractor",
    "ExtractionEvent",
    "StructuredPageContent",
    "ArticleContent",
    "HeadingItem",
    "ExtractedLink",
    "ExtractedImage",
    "ExtractedVideo",
    "ExtractedTable",
    "TableCell",
    "ExtractedForm",
    "ExtractedButton",
    "PageMetadata",
    "AccessibilityInfo",
    "ReadingStats",
    "LinkType",
    "FieldType",
]
