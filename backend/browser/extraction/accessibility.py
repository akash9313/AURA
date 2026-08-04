"""
Accessibility Information Extractor.
Extracts ARIA landmarks, aria-labels, evaluates alt text coverage, and verifies heading hierarchy validity.
"""

import logging
from typing import Dict, List

from browser.extraction.dom_parser import DOMNode
from browser.extraction.models import AccessibilityInfo, HeadingItem

logger = logging.getLogger("AURA.Browser.Extraction.Accessibility")


class AccessibilityExtractor:
    """Extracts accessibility information and audits basic page WCAG compliance metrics."""

    LANDMARK_ROLES = (
        "main", "navigation", "banner", "contentinfo", "search",
        "complementary", "form", "region"
    )

    def extract_accessibility(
        self, root: DOMNode, headings: List[HeadingItem]
    ) -> AccessibilityInfo:
        """
        Extract accessibility metrics from DOM tree.

        Returns:
            AccessibilityInfo object.
        """
        landmarks: List[Dict[str, str]] = []
        aria_labels_count = 0
        total_images = 0
        missing_alt = 0

        self._audit_node(root, landmarks, [0], [0], [0])
        aria_labels_count = self._count_aria_labels(root)
        total_images, missing_alt = self._audit_images(root)

        heading_valid = self._verify_heading_hierarchy(headings)

        return AccessibilityInfo(
            landmarks=landmarks,
            aria_labels_count=aria_labels_count,
            images_missing_alt=missing_alt,
            total_images=total_images,
            heading_hierarchy_valid=heading_valid,
        )

    def _audit_node(
        self,
        node: DOMNode,
        landmarks: List[Dict[str, str]],
        label_counter: List[int],
        img_counter: List[int],
        missing_alt_counter: List[int],
    ) -> None:
        """Recursively scan nodes for landmarks."""
        role = node.get_attribute("role")
        tag = node.tag

        # Check explicit role or implicit HTML5 landmark tag
        if role in self.LANDMARK_ROLES:
            landmarks.append({"role": role, "tag": tag, "id": node.id or ""})
        elif tag in ("main", "nav", "header", "footer", "aside", "form"):
            landmarks.append({"role": tag, "tag": tag, "id": node.id or ""})

        for child in node.children:
            self._audit_node(child, landmarks, label_counter, img_counter, missing_alt_counter)

    def _count_aria_labels(self, node: DOMNode) -> int:
        """Count aria-label attributes in DOM subtree."""
        count = 0
        if node.has_attribute("aria-label") or node.has_attribute("aria-labelledby"):
            count += 1
        for child in node.children:
            count += self._count_aria_labels(child)
        return count

    def _audit_images(self, node: DOMNode) -> Tuple[int, int]:
        """Return (total_images, missing_alt_count)."""
        imgs = node.find_all("img")
        total = len(imgs)
        missing = 0
        for img in imgs:
            alt = img.get_attribute("alt")
            if alt is None or not alt.strip():
                missing += 1
        return total, missing

    def _verify_heading_hierarchy(self, headings: List[HeadingItem]) -> bool:
        """Check if any heading level skips (e.g., H1 directly to H3 without H2)."""
        flat_levels: List[int] = []

        def collect(items: List[HeadingItem]):
            for item in items:
                flat_levels.append(item.level)
                collect(item.children)

        collect(headings)

        if not flat_levels:
            return True

        for i in range(len(flat_levels) - 1):
            curr = flat_levels[i]
            next_lvl = flat_levels[i + 1]
            if next_lvl > curr + 1:
                logger.debug(f"Invalid heading hierarchy: H{curr} followed directly by H{next_lvl}")
                return False

        return True
