import collections
import logging
from typing import Dict, List

logger = logging.getLogger("AURA.Learning.Ranking")


class ToolRankingEngine:
    """
    Ranks tools dynamically based on historical execution frequency and success rate.
    """

    def __init__(self):
        self.tool_counts: Dict[str, int] = collections.defaultdict(int)

    def record_usage(self, tool_name: str) -> None:
        self.tool_counts[tool_name] += 1

    def get_ranked_tools(self) -> List[str]:
        """Return list of tool names sorted by usage frequency descending."""
        sorted_tools = sorted(self.tool_counts.items(), key=lambda x: x[1], reverse=True)
        return [t[0] for t in sorted_tools]

