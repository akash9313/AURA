"""
Readability Article Extractor and Text Metrics Analyzer.
Implements readability scoring to locate primary article content, stripping boilerplate,
and computes reading statistics (word count, sentence count, estimated reading time).
"""

import logging
import re
from typing import List, Optional, Tuple

from browser.extraction.dom_parser import DOMNode
from browser.extraction.models import ArticleContent, ReadingStats

logger = logging.getLogger("AURA.Browser.Extraction.Readability")


class ReadabilityExtractor:
    """
    Locates and extracts primary article content using text-density and DOM element scoring.
    Also calculates reading metrics.
    """

    POSITIVE_PATTERNS = re.compile(
        r"(article|body|content|entry|hentry|main|page|pagination|post|story|text|blog|byline)",
        re.IGNORECASE,
    )
    NEGATIVE_PATTERNS = re.compile(
        r"(combx|comment|community|disqus|extra|foot|header|menu|remark|rss|shoutbox|sidebar|sponsor|ad-break|agegate|pagination|pager|popup)",
        re.IGNORECASE,
    )

    WORDS_PER_MINUTE = 200.0  # Average adult reading speed

    def extract_article(self, root: DOMNode, title_hint: str = "") -> ArticleContent:
        """
        Extract primary article content from cleaned DOM tree.

        Returns:
            ArticleContent object containing paragraphs, quotes, code blocks, lists, and main text.
        """
        best_candidate = self._find_best_candidate(root)
        target_node = best_candidate or root

        paragraphs = []
        lists = []
        quotes = []
        code_blocks = []
        text_lines = []

        self._process_content_nodes(target_node, paragraphs, lists, quotes, code_blocks, text_lines)

        full_text = "\n\n".join(paragraphs) if paragraphs else "\n".join(text_lines)
        byline = self._extract_byline(root)

        return ArticleContent(
            title=title_hint,
            byline=byline,
            text_content=full_text,
            paragraphs=paragraphs,
            lists=lists,
            quotes=quotes,
            code_blocks=code_blocks,
        )

    def calculate_reading_stats(self, article: ArticleContent) -> ReadingStats:
        """Calculate word count, sentence count, paragraph count, and estimated reading time."""
        text = article.text_content or ""
        words = re.findall(r"\b\w+\b", text)
        word_count = len(words)

        # Basic sentence splitting
        sentences = re.split(r"[.!?]+", text)
        sentence_count = len([s for s in sentences if s.strip()])

        paragraph_count = len(article.paragraphs)
        est_minutes = round(word_count / self.WORDS_PER_MINUTE, 2) if word_count > 0 else 0.0

        return ReadingStats(
            word_count=word_count,
            sentence_count=sentence_count,
            paragraph_count=paragraph_count,
            estimated_reading_time_minutes=est_minutes,
        )

    def _find_best_candidate(self, root: DOMNode) -> Optional[DOMNode]:
        """Score container candidates (<article>, <main>, <div>, <section>) to find main content."""
        candidates: List[Tuple[float, DOMNode]] = []

        # Find all container elements
        containers = (
            root.find_all("article")
            + root.find_all("main")
            + root.find_all("div")
            + root.find_all("section")
        )

        for container in containers:
            score = self._score_node(container)
            if score > 0:
                candidates.append((score, container))

        if not candidates:
            return None

        candidates.sort(key=lambda x: x[0], reverse=True)
        best_score, best_node = candidates[0]
        logger.debug(f"Best article container found with score {best_score:.1f}: <{best_node.tag}>")
        return best_node

    def _score_node(self, node: DOMNode) -> float:
        """Score a node based on paragraph count, text density, and class/id hints."""
        score = 0.0

        # Tag-based initial score
        if node.tag == "article":
            score += 25.0
        elif node.tag == "main":
            score += 20.0
        elif node.tag == "section":
            score += 10.0

        # ID and Class pattern bonus/penalty
        identifier = f"{node.id or ''} {node.class_name or ''}"
        if self.POSITIVE_PATTERNS.search(identifier):
            score += 25.0
        if self.NEGATIVE_PATTERNS.search(identifier):
            score -= 25.0

        # Paragraph count & length contribution
        paragraphs = node.find_all("p")
        for p in paragraphs:
            p_text = p.get_text()
            if len(p_text) > 20:
                score += 3.0 + min(len(p_text) / 50.0, 10.0)

        # Link density penalty
        link_density = self._get_link_density(node)
        score *= (1.0 - link_density)

        return score

    def _get_link_density(self, node: DOMNode) -> float:
        """Calculate ratio of link text to total text in a node."""
        text_length = len(node.get_text())
        if text_length == 0:
            return 1.0

        link_text_length = sum(len(link.get_text()) for link in node.find_all("a"))
        return link_text_length / text_length

    def _process_content_nodes(
        self,
        node: DOMNode,
        paragraphs: List[str],
        lists: List[List[str]],
        quotes: List[str],
        code_blocks: List[Dict[str, str]],
        text_lines: List[str],
    ) -> None:
        """Recursively process DOM nodes to populate structured content elements."""
        for child in node.children:
            tag = child.tag
            text = child.get_text().strip()

            if not text and tag not in ("img", "br", "hr"):
                continue

            if tag == "p":
                if len(text) > 10:  # Skip trivial paragraph fragments
                    paragraphs.append(text)
                    text_lines.append(text)
            elif tag in ("ul", "ol"):
                items = [li.get_text().strip() for li in child.find_all("li") if li.get_text().strip()]
                if items:
                    lists.append(items)
                    text_lines.append("\n".join(f"- {it}" for it in items))
            elif tag in ("blockquote", "q"):
                if text:
                    quotes.append(text)
                    text_lines.append(f'"{text}"')
            elif tag == "pre" or tag == "code":
                lang = child.get_attribute("class") or ""
                code_blocks.append({"language": lang, "code": text})
                text_lines.append(f"```\n{text}\n```")
            else:
                self._process_content_nodes(child, paragraphs, lists, quotes, code_blocks, text_lines)

    def _extract_byline(self, root: DOMNode) -> Optional[str]:
        """Locate article author / byline."""
        author_meta = root.find_first("meta")
        # Check byline / author classes
        for tag in ("span", "div", "a", "p"):
            nodes = root.find_all(tag)
            for node in nodes:
                ident = f"{node.id or ''} {node.class_name or ''}"
                if "byline" in ident.lower() or "author" in ident.lower():
                    txt = node.get_text().strip()
                    if txt and len(txt) < 100:
                        return txt
        return None
