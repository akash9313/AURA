"""
DOM Intelligence & Content Extraction Service.
Exposes high-level extraction API for downstream Workflow Engine and LLMs.
Publishes extraction lifecycle events to the AURA EventBus.
"""

import logging
from typing import Any, Dict, Optional

from core.service import Service
from browser.extraction.content_extractor import ContentExtractor
from browser.extraction.events import ExtractionEvent
from browser.extraction.models import StructuredPageContent

logger = logging.getLogger("AURA.Browser.Extraction.Service")


class DOMExtractionService(Service):
    """
    DOM Intelligence Extraction Service.
    Converts web page HTML into structured semantic objects (StructuredPageContent).
    Ensures zero raw HTML clutter is passed to LLMs.
    """

    def __init__(self, bus: Any = None):
        super().__init__(bus)
        self.extractor = ContentExtractor()
        logger.info("DOMExtractionService initialized")

    def extract_from_html(self, html_content: str, url: str = "") -> StructuredPageContent:
        """
        Extract structured page content from raw HTML.

        Args:
            html_content: Raw HTML text.
            url: Page URL.

        Returns:
            StructuredPageContent object.
        """
        try:
            content = self.extractor.extract(html_content, url=url)

            # Publish extraction events to EventBus
            if self.bus:
                self.bus.publish(
                    ExtractionEvent.CONTENT_EXTRACTED.value,
                    {"url": url, "title": content.title, "extraction_time_ms": content.extraction_time_ms},
                )

                if content.main_content and content.main_content.text_content:
                    self.bus.publish(
                        ExtractionEvent.ARTICLE_FOUND.value,
                        {"url": url, "title": content.title, "word_count": content.reading_stats.word_count},
                    )

                if content.tables:
                    self.bus.publish(
                        ExtractionEvent.TABLE_FOUND.value,
                        {"url": url, "count": len(content.tables)},
                    )

                if content.forms:
                    self.bus.publish(
                        ExtractionEvent.FORM_FOUND.value,
                        {"url": url, "count": len(content.forms)},
                    )

                if content.images or content.videos:
                    self.bus.publish(
                        ExtractionEvent.MEDIA_FOUND.value,
                        {"url": url, "images_count": len(content.images), "videos_count": len(content.videos)},
                    )

            return content

        except Exception as e:
            logger.error(f"DOM Content Extraction failed: {e}")
            if self.bus:
                self.bus.publish(
                    ExtractionEvent.EXTRACTION_FAILED.value,
                    {"url": url, "error": str(e)},
                )
            # Return graceful fallback empty StructuredPageContent
            return StructuredPageContent(
                url=url,
                title="Extraction Error",
                description=str(e),
            )

    def start(self) -> None:
        logger.info("DOMExtractionService starting...")

    def stop(self) -> None:
        logger.info("DOMExtractionService stopping...")

    def is_healthy(self) -> bool:
        return True
