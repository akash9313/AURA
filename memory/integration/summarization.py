import logging
from typing import Any, Dict, List, Tuple

logger = logging.getLogger("AURA.Memory.Integration.Summarization")


class MissionSummarizer:
    def summarize_mission(
        self,
        goal: str,
        status: str,
        capabilities_used: List[str],
        verification_evidence: Dict[str, Any],
        reflection_report: Dict[str, Any],
        recovery_attempts: int = 0,
    ) -> Tuple[str, List[str]]:
        lessons: List[str] = []

        if status == "completed":
            summary = f"Mission '{goal}' completed successfully using capabilities: {', '.join(capabilities_used)}."
            lessons.append(f"Goal '{goal}' is effectively achievable using sequence: {capabilities_used}")
            if recovery_attempts > 0:
                lessons.append(f"Required {recovery_attempts} recovery attempts due to transient UI/network state.")
        else:
            summary = f"Mission '{goal}' failed during execution."
            lessons.append(f"Goal '{goal}' encountered failures. Review capability chain: {capabilities_used}")

        if "lessons_learned" in reflection_report and isinstance(reflection_report["lessons_learned"], list):
            for item in reflection_report["lessons_learned"]:
                if item not in lessons:
                    lessons.append(str(item))

        return summary, lessons
