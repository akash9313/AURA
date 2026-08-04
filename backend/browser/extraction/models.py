"""
DOM Intelligence & Content Extraction Domain Models.
Provider-independent structured representations of web page content for downstream LLM and Workflow Engine consumption.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import time


class LinkType(Enum):
    """Classification of hyperlinks."""
    INTERNAL = "internal"
    EXTERNAL = "external"
    NOFOLLOW = "nofollow"
    DOWNLOAD = "download"
    ANCHOR = "anchor"


class FieldType(Enum):
    """Types of form input fields."""
    TEXT = "text"
    PASSWORD = "password"
    EMAIL = "email"
    NUMBER = "number"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    SELECT = "select"
    TEXTAREA = "textarea"
    SUBMIT = "submit"
    BUTTON = "button"
    HIDDEN = "hidden"
    FILE = "file"
    OTHER = "other"


@dataclass
class HeadingItem:
    """Single heading element in document outline."""
    level: int  # 1 to 6 for H1..H6
    text: str
    heading_id: Optional[str] = None
    children: List["HeadingItem"] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level,
            "text": self.text,
            "heading_id": self.heading_id,
            "children": [c.to_dict() for c in self.children],
        }


@dataclass
class ExtractedLink:
    """Single hyperlink on the page."""
    text: str
    url: str
    link_type: LinkType
    is_nofollow: bool = False
    title: Optional[str] = None
    target: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "url": self.url,
            "link_type": self.link_type.value,
            "is_nofollow": self.is_nofollow,
            "title": self.title,
            "target": self.target,
        }


@dataclass
class ExtractedImage:
    """Single image element."""
    src: str
    alt: str = ""
    caption: Optional[str] = None
    title: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "src": self.src,
            "alt": self.alt,
            "caption": self.caption,
            "title": self.title,
            "width": self.width,
            "height": self.height,
        }


@dataclass
class ExtractedVideo:
    """Single video element or iframe embed."""
    src: str
    poster: Optional[str] = None
    title: Optional[str] = None
    provider: Optional[str] = None  # e.g., 'youtube', 'vimeo', 'html5'

    def to_dict(self) -> Dict[str, Any]:
        return {
            "src": self.src,
            "poster": self.poster,
            "title": self.title,
            "provider": self.provider,
        }


@dataclass
class TableCell:
    """Single cell within a table."""
    text: str
    is_header: bool = False
    colspan: int = 1
    rowspan: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "is_header": self.is_header,
            "colspan": self.colspan,
            "rowspan": self.rowspan,
        }


@dataclass
class ExtractedTable:
    """Structured tabular data extracted from a page."""
    headers: List[str] = field(default_factory=list)
    rows: List[List[str]] = field(default_factory=list)
    caption: Optional[str] = None
    table_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "headers": self.headers,
            "rows": self.rows,
            "caption": self.caption,
            "table_id": self.table_id,
            "row_count": len(self.rows),
            "column_count": len(self.headers) if self.headers else (len(self.rows[0]) if self.rows else 0),
        }


@dataclass
class FormField:
    """Single input element within a form."""
    field_type: FieldType
    name: Optional[str] = None
    field_id: Optional[str] = None
    label: Optional[str] = None
    value: Optional[str] = None
    placeholder: Optional[str] = None
    required: bool = False
    options: List[str] = field(default_factory=list)  # for select dropdowns or radio groups

    def to_dict(self) -> Dict[str, Any]:
        return {
            "field_type": self.field_type.value,
            "name": self.name,
            "field_id": self.field_id,
            "label": self.label,
            "value": self.value,
            "placeholder": self.placeholder,
            "required": self.required,
            "options": self.options,
        }


@dataclass
class ExtractedForm:
    """Form element containing inputs and action metadata."""
    form_id: Optional[str] = None
    name: Optional[str] = None
    action: Optional[str] = None
    method: str = "GET"
    fields: List[FormField] = field(default_factory=list)
    submit_buttons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "form_id": self.form_id,
            "name": self.name,
            "action": self.action,
            "method": self.method,
            "fields": [f.to_dict() for f in self.fields],
            "submit_buttons": self.submit_buttons,
        }


@dataclass
class ExtractedButton:
    """Interactive button element."""
    text: str
    button_type: str = "button"
    button_id: Optional[str] = None
    name: Optional[str] = None
    aria_label: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "button_type": self.button_type,
            "button_id": self.button_id,
            "name": self.name,
            "aria_label": self.aria_label,
        }


@dataclass
class PageMetadata:
    """Metadata tags extracted from HTML head."""
    description: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    author: Optional[str] = None
    published_date: Optional[str] = None
    modified_date: Optional[str] = None
    language: Optional[str] = None
    canonical_url: Optional[str] = None
    open_graph: Dict[str, str] = field(default_factory=dict)
    twitter_card: Dict[str, str] = field(default_factory=dict)
    schema_org: List[Dict[str, Any]] = field(default_factory=list)
    charset: str = "utf-8"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "keywords": self.keywords,
            "author": self.author,
            "published_date": self.published_date,
            "modified_date": self.modified_date,
            "language": self.language,
            "canonical_url": self.canonical_url,
            "open_graph": self.open_graph,
            "twitter_card": self.twitter_card,
            "schema_org": self.schema_org,
            "charset": self.charset,
        }


@dataclass
class AccessibilityInfo:
    """Accessibility landmarks and audit metrics."""
    landmarks: List[Dict[str, str]] = field(default_factory=list)
    aria_labels_count: int = 0
    images_missing_alt: int = 0
    total_images: int = 0
    heading_hierarchy_valid: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "landmarks": self.landmarks,
            "aria_labels_count": self.aria_labels_count,
            "images_missing_alt": self.images_missing_alt,
            "total_images": self.total_images,
            "alt_text_coverage_percent": (
                round((1.0 - (self.images_missing_alt / self.total_images)) * 100, 1)
                if self.total_images > 0
                else 100.0
            ),
            "heading_hierarchy_valid": self.heading_hierarchy_valid,
        }


@dataclass
class ReadingStats:
    """Article readability statistics."""
    word_count: int = 0
    sentence_count: int = 0
    paragraph_count: int = 0
    estimated_reading_time_minutes: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "word_count": self.word_count,
            "sentence_count": self.sentence_count,
            "paragraph_count": self.paragraph_count,
            "estimated_reading_time_minutes": self.estimated_reading_time_minutes,
        }


@dataclass
class ArticleContent:
    """Cleaned primary article content."""
    title: str = ""
    byline: Optional[str] = None
    text_content: str = ""
    paragraphs: List[str] = field(default_factory=list)
    lists: List[List[str]] = field(default_factory=list)
    quotes: List[str] = field(default_factory=list)
    code_blocks: List[Dict[str, str]] = field(default_factory=list)  # list of {'language': ..., 'code': ...}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "byline": self.byline,
            "text_content": self.text_content,
            "paragraph_count": len(self.paragraphs),
            "list_count": len(self.lists),
            "quote_count": len(self.quotes),
            "code_block_count": len(self.code_blocks),
        }


@dataclass
class StructuredPageContent:
    """
    Complete structured representation of a web page.
    This is the primary object returned to downstream systems (Workflow Engine / LLM).
    Exposes zero raw HTML clutter.
    """
    url: str
    title: str
    description: Optional[str] = None
    language: Optional[str] = None
    author: Optional[str] = None
    published_date: Optional[str] = None
    main_content: ArticleContent = field(default_factory=ArticleContent)
    headings: List[HeadingItem] = field(default_factory=list)
    links: List[ExtractedLink] = field(default_factory=list)
    images: List[ExtractedImage] = field(default_factory=list)
    videos: List[ExtractedVideo] = field(default_factory=list)
    tables: List[ExtractedTable] = field(default_factory=list)
    forms: List[ExtractedForm] = field(default_factory=list)
    buttons: List[ExtractedButton] = field(default_factory=list)
    metadata: PageMetadata = field(default_factory=PageMetadata)
    accessibility: AccessibilityInfo = field(default_factory=AccessibilityInfo)
    reading_stats: ReadingStats = field(default_factory=ReadingStats)
    extraction_time_ms: float = 0.0
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "title": self.title,
            "description": self.description,
            "language": self.language,
            "author": self.author,
            "published_date": self.published_date,
            "main_content": self.main_content.to_dict(),
            "headings": [h.to_dict() for h in self.headings],
            "link_count": len(self.links),
            "image_count": len(self.images),
            "video_count": len(self.videos),
            "table_count": len(self.tables),
            "form_count": len(self.forms),
            "button_count": len(self.buttons),
            "metadata": self.metadata.to_dict(),
            "accessibility": self.accessibility.to_dict(),
            "reading_stats": self.reading_stats.to_dict(),
            "extraction_time_ms": self.extraction_time_ms,
            "timestamp": self.timestamp,
        }
