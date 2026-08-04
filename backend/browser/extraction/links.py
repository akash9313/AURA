"""
Hyperlink Extractor.
Extracts anchor tags, resolves relative URLs, classifies links as internal, external,
nofollow, or download, and extracts titles and target metadata.
"""

import logging
import re
from typing import List, Optional
from urllib.parse import urljoin, urlparse

from browser.extraction.dom_parser import DOMNode
from browser.extraction.models import ExtractedLink, LinkType

logger = logging.getLogger("AURA.Browser.Extraction.Links")


class LinkExtractor:
    """Extracts and classifies hyperlinks from DOM tree."""

    DOWNLOAD_EXTENSIONS = (
        ".pdf", ".zip", ".tar", ".gz", ".7z", ".rar", ".exe", ".dmg",
        ".iso", ".csv", ".xlsx", ".docx", ".pptx", ".mp3", ".mp4"
    )

    def extract_links(self, root: DOMNode, base_url: str = "") -> List[ExtractedLink]:
        """
        Extract all links from anchor tags.

        Args:
            root: Root DOMNode.
            base_url: Base URL of current page for relative resolution.

        Returns:
            List of ExtractedLink objects.
        """
        link_nodes = root.find_all("a")
        extracted: List[ExtractedLink] = []

        base_parsed = urlparse(base_url) if base_url else None
        base_domain = base_parsed.netloc.lower() if base_parsed else ""

        for node in link_nodes:
            href = node.get_attribute("href")
            if not href:
                continue

            href = href.strip()
            if href.startswith("javascript:") or href.startswith("mailto:") or href.startswith("tel:"):
                continue

            # Resolve relative URL
            full_url = urljoin(base_url, href) if base_url else href
            text = node.get_text().strip()
            rel = (node.get_attribute("rel") or "").lower()
            is_nofollow = "nofollow" in rel
            title = node.get_attribute("title")
            target = node.get_attribute("target")

            # Determine link type
            link_type = self._classify_link_type(full_url, base_domain, is_nofollow, node)

            extracted.append(
                ExtractedLink(
                    text=text or title or full_url,
                    url=full_url,
                    link_type=link_type,
                    is_nofollow=is_nofollow,
                    title=title,
                    target=target,
                )
            )

        logger.debug(f"Extracted {len(extracted)} links (base: '{base_url}')")
        return extracted

    def _classify_link_type(self, url: str, base_domain: str, is_nofollow: bool, node: DOMNode) -> LinkType:
        """Classify link into INTERNAL, EXTERNAL, NOFOLLOW, DOWNLOAD, or ANCHOR."""
        if url.startswith("#"):
            return LinkType.ANCHOR

        # Check for explicit download attribute or file extension
        if node.has_attribute("download") or any(url.lower().endswith(ext) for ext in self.DOWNLOAD_EXTENSIONS):
            return LinkType.DOWNLOAD

        if is_nofollow:
            return LinkType.NOFOLLOW

        parsed = urlparse(url)
        target_domain = parsed.netloc.lower()

        if base_domain and target_domain and target_domain != base_domain:
            return LinkType.EXTERNAL

        return LinkType.INTERNAL
