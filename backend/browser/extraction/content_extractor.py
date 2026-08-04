"""
Intelligent DOM & Content Extraction Orchestrator.
Converts web pages into rich, structured, AI-friendly data objects (StructuredPageContent).
Guarantees fast extraction under 300 ms for typical pages with zero raw HTML clutter.
"""

import logging
import time
from typing import Optional

from browser.extraction.accessibility import AccessibilityExtractor
from browser.extraction.dom_parser import DOMParser
from browser.extraction.forms import FormExtractor
from browser.extraction.headings import HeadingsExtractor
from browser.extraction.links import LinkExtractor
from browser.extraction.media import MediaExtractor
from browser.extraction.metadata import MetadataExtractor
from browser.extraction.models import StructuredPageContent
from browser.extraction.readability import ReadabilityExtractor
from browser.extraction.tables import TableExtractor

logger = logging.getLogger("AURA.Browser.Extraction.ContentExtractor")


class ContentExtractor:
    """
    DOM Content Extractor.
    Applies specialized extractors to convert raw HTML into a clean StructuredPageContent object.
    """

    def __init__(self):
        self.dom_parser = DOMParser()
        self.metadata_extractor = MetadataExtractor()
        self.readability_extractor = ReadabilityExtractor()
        self.headings_extractor = HeadingsExtractor()
        self.link_extractor = LinkExtractor()
        self.media_extractor = MediaExtractor()
        self.table_extractor = TableExtractor()
        self.form_extractor = FormExtractor()
        self.accessibility_extractor = AccessibilityExtractor()

    def extract(self, html_content: str, url: str = "") -> StructuredPageContent:
        """
        Extract structured semantic content from raw HTML.

        Args:
            html_content: Raw HTML text of the page.
            url: Page URL for link resolution and metadata fallback.

        Returns:
            StructuredPageContent object.
        """
        start_time = time.time()

        # Parse DOM tree and prune clutter
        root = self.dom_parser.parse(html_content, strip_clutter=True)

        # Extract metadata
        metadata = self.metadata_extractor.extract_metadata(root, base_url=url)

        # Derive page title (from metadata OG / title or root title tag)
        title = (
            (metadata.open_graph.get("title") if metadata.open_graph else None)
            or (metadata.twitter_card.get("title") if metadata.twitter_card else None)
            or self._extract_title_tag(root)
            or "Untitled Page"
        )

        # Extract primary article content & readability stats
        main_content = self.readability_extractor.extract_article(root, title_hint=title)
        reading_stats = self.readability_extractor.calculate_reading_stats(main_content)

        # Extract document outline
        headings = self.headings_extractor.extract_headings(root)

        # Extract links
        links = self.link_extractor.extract_links(root, base_url=url)

        # Extract media (images and videos)
        images, videos = self.media_extractor.extract_media(root, base_url=url)

        # Extract tables
        tables = self.table_extractor.extract_tables(root)

        # Extract forms and buttons
        forms, buttons = self.form_extractor.extract_forms_and_buttons(root)

        # Extract accessibility information
        accessibility = self.accessibility_extractor.extract_accessibility(root, headings)

        extraction_time_ms = round((time.time() - start_time) * 1000, 2)
        logger.info(
            f"Content extraction completed for '{url or title}' in {extraction_time_ms}ms "
            f"({reading_stats.word_count} words, {len(links)} links, {len(images)} images, {len(tables)} tables, {len(forms)} forms)"
        )

        return StructuredPageContent(
            url=url,
            title=title,
            description=metadata.description,
            language=metadata.language,
            author=metadata.author,
            published_date=metadata.published_date,
            main_content=main_content,
            headings=headings,
            links=links,
            images=images,
            videos=videos,
            tables=tables,
            forms=forms,
            buttons=buttons,
            metadata=metadata,
            accessibility=accessibility,
            reading_stats=reading_stats,
            extraction_time_ms=extraction_time_ms,
        )

    def _extract_title_tag(self, root) -> Optional[str]:
        title_node = root.find_first("title")
        if title_node:
            return title_node.get_text().strip()
        return None
