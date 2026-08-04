import logging
from typing import Dict, List, Optional
from monitoring.models import MetricRecord, SystemHealthStatus

logger = logging.getLogger("AURA.Monitoring.Dashboard")


class LocalDashboardRenderer:
    """Renders local CLI developer observability dashboard."""

    def render_summary(self, metrics: List[MetricRecord], health: SystemHealthStatus) -> str:
        lines = [
            "==================================================",
            "        AURA PERFORMANCE TELEMETRY DASHBOARD      ",
            "==================================================",
            f"Health Status: {health.status.value.upper()}",
            f"Active Services: {len(health.services)}",
            "--------------------------------------------------"
        ]

        if health.warnings:
            lines.append("Warnings:")
            for w in health.warnings:
                lines.append(f"  ! {w}")
            lines.append("--------------------------------------------------")

        lines.append("Recent Latency & Pipeline Metrics:")
        for m in metrics[-10:]:
            lines.append(f"  - {m.name}: {m.value:.2f} {m.unit}")

        lines.append("==================================================")
        summary_text = "\n".join(lines)
        return summary_text
