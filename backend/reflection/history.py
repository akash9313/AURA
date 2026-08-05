"""
Reflection History Store.
Persists past reflection reports and workflow execution telemetry for trend analysis across workflows.
"""

import logging
from typing import Dict, List, Optional

from reflection.models import ReflectionReport

logger = logging.getLogger("AURA.Reflection.History")


class ReflectionHistoryStore:
    """
    In-memory store for historical reflection reports.
    """

    def __init__(self):
        self._reports: Dict[str, ReflectionReport] = {}

    def save_report(self, report: ReflectionReport) -> None:
        """Save report."""
        self._reports[report.report_id] = report
        logger.info(f"Saved ReflectionReport '{report.report_id}' for workflow '{report.workflow_id}'")

    def get_report(self, report_id: str) -> Optional[ReflectionReport]:
        """Get report by ID."""
        return self._reports.get(report_id)

    def list_reports(self) -> List[ReflectionReport]:
        """List all reports."""
        return list(self._reports.values())
