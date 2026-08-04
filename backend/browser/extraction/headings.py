"""
Document Outline and Headings Extractor.
Extracts H1..H6 heading tags and builds a nested, hierarchical Document Outline.
"""

import logging
from typing import List, Optional

from browser.extraction.dom_parser import DOMNode
from browser.extraction.models import HeadingItem

logger = logging.getLogger("AURA.Browser.Extraction.Headings")


class HeadingsExtractor:
    """Extracts document headings and builds a hierarchical document outline tree."""

    HEADING_TAGS = ("h1", "h2", "h3", "h4", "h5", "h6")

    def extract_headings(self, root: DOMNode) -> List[HeadingItem]:
        """
        Extract flat list of headings and structure them into a nested hierarchy tree.

        Returns:
            List of top-level HeadingItem objects with nested children.
        """
        flat_headings: List[HeadingItem] = []

        self._find_heading_nodes(root, flat_headings)

        if not flat_headings:
            return []

        tree = self._build_heading_tree(flat_headings)
        logger.debug(f"Built document outline with {len(flat_headings)} total headings")
        return tree

    def _find_heading_nodes(self, node: DOMNode, flat_list: List[HeadingItem]) -> None:
        """Traverse DOM tree sequentially to gather heading nodes in document order."""
        for child in node.children:
            if child.tag in self.HEADING_TAGS:
                level = int(child.tag[1])
                text = child.get_text().strip()
                if text:
                    flat_list.append(
                        HeadingItem(
                            level=level,
                            text=text,
                            heading_id=child.id,
                        )
                    )
            self._find_heading_nodes(child, flat_list)

    def _build_heading_tree(self, flat_headings: List[HeadingItem]) -> List[HeadingItem]:
        """Convert flat list of headings into a nested tree based on levels."""
        root_items: List[HeadingItem] = []
        stack: List[HeadingItem] = []

        for item in flat_headings:
            while stack and stack[-1].level >= item.level:
                stack.pop()

            if stack:
                stack[-1].children.append(item)
            else:
                root_items.append(item)

            stack.append(item)

        return root_items
