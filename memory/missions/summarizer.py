import logging
from typing import List, Tuple

from memory.missions.models import MissionRecord

logger = logging.getLogger("AURA.Memory.Missions.Summarizer")


class MissionSummarizer:
    def summarize_mission(self, record: MissionRecord) -> Tuple[str, List[str]]:
        status_str = "succeeded" if record.status == "completed" else "failed"
        caps_str = ", ".join(record.capabilities_used) if record.capabilities_used else "none"

        summary = f"Mission '{record.goal}' {status_str} in {record.duration_ms}ms using capabilities [{caps_str}]."

        lessons = []
        if record.failures:
            lessons.append(f"Encountered failure: {record.failures[0]}. Verify preconditions in advance.")
        if record.recoveries:
            lessons.append(f"Successfully recovered via checkpoint restoration: {record.recoveries[0]}.")
        if not lessons:
            lessons.append("Standard execution path completed without operational anomalies.")

        return (summary, lessons)
