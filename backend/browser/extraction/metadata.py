"""
HTML Metadata Extractor.
Extracts Open Graph, Twitter Cards, Schema.org JSON-LD microdata, Canonical URLs,
author, language, published dates, and charset from HTML head tags.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional

from browser.extraction.dom_parser import DOMNode
from browser.extraction.models import PageMetadata

logger = logging.getLogger("AURA.Browser.Extraction.Metadata")


class MetadataExtractor:
    """Extracts rich metadata from DOM tree."""

    def extract_metadata(self, root: DOMNode, base_url: str = "") -> PageMetadata:
        """
        Extract metadata from head elements, OpenGraph, Twitter Cards, and Schema.org JSON-LD.

        Returns:
            PageMetadata object.
        """
        meta_nodes = root.find_all("meta")

        description: Optional[str] = None
        keywords: List[str] = []
        author: Optional[str] = None
        published_date: Optional[str] = None
        modified_date: Optional[str] = None
        canonical_url: Optional[str] = None
        charset: str = "utf-8"

        open_graph: Dict[str, str] = {}
        twitter_card: Dict[str, str] = {}
        schema_org: List[Dict[str, Any]] = []

        # Extract html lang attribute
        html_node = root.find_first("html")
        language = html_node.get_attribute("lang") if html_node else None

        # Extract canonical URL
        link_nodes = root.find_all("link")
        for link in link_nodes:
            rel = link.get_attribute("rel") or ""
            if rel.lower() == "canonical":
                canonical_url = link.get_attribute("href")
                break

        # Process meta tags
        for m in meta_nodes:
            name = (m.get_attribute("name") or "").lower()
            prop = (m.get_attribute("property") or "").lower()
            content = m.get_attribute("content") or ""
            c_set = m.get_attribute("charset")

            if c_set:
                charset = c_set.lower()

            if not content:
                continue

            # OpenGraph
            if prop.startswith("og:"):
                key = prop[3:]
                open_graph[key] = content
                if key == "description" and not description:
                    description = content
                elif key == "published_time" and not published_date:
                    published_date = content
                elif key == "modified_time" and not modified_date:
                    modified_date = content

            # Twitter Cards
            elif name.startswith("twitter:"):
                key = name[8:]
                twitter_card[key] = content

            # Standard Meta
            elif name == "description":
                if not description:
                    description = content
            elif name == "keywords":
                keywords = [k.strip() for k in content.split(",") if k.strip()]
            elif name in ("author", "article:author"):
                if not author:
                    author = content
            elif name in ("pubdate", "publishdate", "article:published_time", "date"):
                if not published_date:
                    published_date = content
            elif name in ("lastmod", "article:modified_time", "updated_time"):
                if not modified_date:
                    modified_date = content

        # Extract Schema.org JSON-LD
        schema_org = self._extract_json_ld(root)

        # Supplement author / published_date from Schema.org if missing
        if schema_org:
            for item in schema_org:
                if isinstance(item, dict):
                    if not author and "author" in item:
                        auth_val = item["author"]
                        author = auth_val.get("name") if isinstance(auth_val, dict) else str(auth_val)
                    if not published_date and "datePublished" in item:
                        published_date = str(item["datePublished"])
                    if not description and "description" in item:
                        description = str(item["description"])

        return PageMetadata(
            description=description,
            keywords=keywords,
            author=author,
            published_date=published_date,
            modified_date=modified_date,
            language=language,
            canonical_url=canonical_url or base_url,
            open_graph=open_graph,
            twitter_card=twitter_card,
            schema_org=schema_org,
            charset=charset,
        )

    def _extract_json_ld(self, root: DOMNode) -> List[Dict[str, Any]]:
        """Extract and parse Schema.org JSON-LD scripts."""
        results: List[Dict[str, Any]] = []
        script_nodes = root.find_all("script")

        for s in script_nodes:
            stype = (s.get_attribute("type") or "").lower()
            if "application/ld+json" in stype:
                text = s.get_text().strip()
                if text:
                    try:
                        data = json.loads(text)
                        if isinstance(data, list):
                            results.extend(data)
                        elif isinstance(data, dict):
                            results.append(data)
                    except Exception as e:
                        logger.debug(f"JSON-LD parse warning: {e}")

        return results
