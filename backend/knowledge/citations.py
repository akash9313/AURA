import logging
from typing import List
from knowledge.models import CitationInfo

logger = logging.getLogger("AURA.Knowledge.Citations")


class CitationFormatter:
    """Formats markdown source citations and reference footnotes."""

    def format_citations(self, citations: List[CitationInfo]) -> str:
        if not citations:
            return ""

        lines = ["\n### References & Citations"]
        for idx, cite in enumerate(citations, 1):
            lines.append(f"[{idx}] **{cite.source_title}** — \"{cite.excerpt[:80]}...\"")

        return "\n".join(lines)
