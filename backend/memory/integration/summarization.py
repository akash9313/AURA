"""
Mission Summarizer.
Distills completed workflow metrics, Goal Verification empirical evidence, and Reflection Engine reports into operational lessons learned.
"""

import logging
from typing import Any, Dict, List, Tuple

logger = logging.getLogger("AURA.Memory.Integration.Summarization")


class MissionSummarizer:
    """
    Summarizes mission execution data and distills operational lessons.
    """

    def summarize_mission(
        self,
        goal: str,
        status: str,
        capabilities_used: List[str],
        verification_evidence: Dict[str, Any],
        reflection_report: Dict[str, Any],
        recovery_attempts: int = 0,
    ) -> Tuple[str, List[str]]:
        """
        Produce human-readable operational summary and extracted lessons learned.

        Args:
            goal: Natural language goal.
            status: Execution status string.
            capabilities_used: Capabilities involved in execution.
            verification_evidence: Empirical evidence dict.
            reflection_report: Reflection engine output dict.
            recovery_attempts: Count of recovery retries used.

        Returns:
            Tuple of (summary_string, lessons_learned_list).
        """
        logger.info(f"Summarizing mission execution for goal: '{goal}'...")

        lessons: List[str] = []

        if status == "completed":
            summary = f"Mission '{goal}' completed successfully using capabilities: {', '.join(capabilities_used)}."
            lessons.append(f"Goal '{goal}' is effectively achievable using sequence: {capabilities_used}")
            if recovery_attempts > 0:
                lessons.append(f"Required {recovery_attempts} recovery attempts due to transient UI/network state.")
        else:
            summary = f"Mission '{goal}' failed during execution."
            lessons.append(f"Goal '{goal}' encountered failures. Review capability chain: {capabilities_used}")

        # Incorporate reflection report insights if available
        if "lessons_learned" in reflection_report and isinstance(reflection_report["lessons_learned"], list):
            for item in reflection_report["lessons_learned"]:
                if item not in lessons:
                    lessons.append(str(item))

        return summary, lessons
