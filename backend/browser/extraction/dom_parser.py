"""
Lightweight DOM Parser and DOM Cleaner.
Parses raw HTML into a clean internal DOM tree, stripping boilerplate, advertisements, cookie banners,
navigation menus, footers, sidebars, tracking elements, scripts, styles, and hidden elements.
"""

import logging
import re
from html.parser import HTMLParser
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger("AURA.Browser.Extraction.DOMParser")


class DOMNode:
    """Lightweight in-memory DOM element node."""

    def __init__(self, tag: str, attrs: Optional[Dict[str, str]] = None, parent: Optional["DOMNode"] = None):
        self.tag = tag.lower()
        self.attrs = attrs or {}
        self.parent = parent
        self.children: List[DOMNode] = []
        self.text_content: str = ""
        self.tail_text: str = ""

    @property
    def id(self) -> Optional[str]:
        return self.attrs.get("id")

    @property
    def class_name(self) -> str:
        return self.attrs.get("class", "")

    def get_attribute(self, attr: str) -> Optional[str]:
        return self.attrs.get(attr.lower())

    def has_attribute(self, attr: str) -> bool:
        return attr.lower() in self.attrs

    def get_text(self, strip: bool = True) -> str:
        """Recursively assemble all inner text of this node and its descendants."""
        parts = []
        if self.text_content:
            parts.append(self.text_content)
        for child in self.children:
            child_text = child.get_text(strip=False)
            if child_text:
                parts.append(child_text)
            if child.tail_text:
                parts.append(child.tail_text)
        raw = " ".join(parts)
        if strip:
            return re.sub(r"\s+", " ", raw).strip()
        return raw

    def find_all(self, tag: str) -> List["DOMNode"]:
        """Find all descendant nodes matching a given tag."""
        target_tag = tag.lower()
        results = []
        for child in self.children:
            if child.tag == target_tag:
                results.append(child)
            results.extend(child.find_all(target_tag))
        return results

    def find_first(self, tag: str) -> Optional["DOMNode"]:
        """Find first descendant matching a given tag."""
        target_tag = tag.lower()
        for child in self.children:
            if child.tag == target_tag:
                return child
            found = child.find_first(target_tag)
            if found:
                return found
        return None


class DOMTreeBuilder(HTMLParser):
    """
    HTMLParser subclass building a DOMNode tree.
    Handles malformed HTML, unclosed tags, and special entities gracefully.
    """

    VOID_ELEMENTS: Set[str] = {
        "area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr"
    }

    IGNORE_TAGS: Set[str] = {
        "script", "style", "noscript", "svg", "canvas", "template"
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = DOMNode("root")
        self.current = self.root
        self.ignored_depth = 0

    def handle_starttag(self, tag: str, attrs: List[tuple]):
        tag_lower = tag.lower()
        attr_dict = {k.lower(): v or "" for k, v in attrs}

        if tag_lower in self.IGNORE_TAGS:
            self.ignored_depth += 1
            return

        if self.ignored_depth > 0:
            return

        node = DOMNode(tag_lower, attrs=attr_dict, parent=self.current)
        self.current.children.append(node)

        if tag_lower not in self.VOID_ELEMENTS:
            self.current = node

    def handle_endtag(self, tag: str):
        tag_lower = tag.lower()
        if tag_lower in self.IGNORE_TAGS:
            if self.ignored_depth > 0:
                self.ignored_depth -= 1
            return

        if self.ignored_depth > 0:
            return

        # Ascend tree to matching tag if possible
        curr = self.current
        while curr is not self.root:
            if curr.tag == tag_lower:
                self.current = curr.parent if curr.parent else self.root
                break
            curr = curr.parent

    def handle_data(self, data: str):
        if self.ignored_depth > 0:
            return

        if not data or not data.strip():
            return

        if self.current.children:
            self.current.children[-1].tail_text += " " + data.strip()
        else:
            self.current.text_content += " " + data.strip()


class DOMParser:
    """
    Parses raw HTML and strips clutter elements (ads, banners, navs, footers, sidebars).
    """

    CLUTTER_PATTERNS = re.compile(
        r"(ad|banner|cookie|consent|notice|popup|overlay|modal|nav|footer|sidebar|share|social|newsletter|widget|tracking|promo)",
        re.IGNORECASE,
    )

    def parse(self, html_content: str, strip_clutter: bool = True) -> DOMNode:
        """
        Parse raw HTML into a DOMNode tree.

        Args:
            html_content: Raw HTML text.
            strip_clutter: If True, prunes navigation, footers, ads, and cookie banners.

        Returns:
            Root DOMNode.
        """
        if not html_content or not isinstance(html_content, str):
            return DOMNode("root")

        try:
            builder = DOMTreeBuilder()
            builder.feed(html_content)
            root = builder.root
        except Exception as e:
            logger.warning(f"HTMLParser error, returning empty root: {e}")
            return DOMNode("root")

        if strip_clutter:
            self.prune_clutter(root)

        return root

    def prune_clutter(self, node: DOMNode) -> None:
        """Recursively remove noise elements from DOM tree."""
        filtered_children = []
        for child in node.children:
            if self._is_clutter_node(child):
                logger.debug(f"Pruned clutter node: <{child.tag} id='{child.id}' class='{child.class_name}'>")
                continue
            self.prune_clutter(child)
            filtered_children.append(child)
        node.children = filtered_children

    def _is_clutter_node(self, node: DOMNode) -> bool:
        """Check if node matches boilerplate noise or clutter patterns."""
        tag = node.tag

        # Always prune navigation, footer, header (unless header inside article), sidebar, etc.
        if tag in ("nav", "footer", "aside"):
            return True

        # Check aria roles
        role = node.get_attribute("role")
        if role in ("navigation", "contentinfo", "banner", "complementary", "dialog"):
            return True

        # Check style for hidden
        style = node.get_attribute("style") or ""
        if "display: none" in style.lower() or "visibility: hidden" in style.lower():
            return True

        # Check class and ID against clutter regex
        identifier = f"{node.id or ''} {node.class_name or ''}"
        if identifier.strip() and self.CLUTTER_PATTERNS.search(identifier):
            # Exception: if it's main content wrapper like 'article-body' or 'main-content'
            if re.search(r"(article-body|main-content|post-content|entry-content)", identifier, re.IGNORECASE):
                return False
            # If tag is section or div with ad/cookie/banner/nav/footer/sidebar in name
            if re.search(r"(ad|banner|cookie|consent|footer|sidebar|widget|promo)", identifier, re.IGNORECASE):
                return True

        return False
