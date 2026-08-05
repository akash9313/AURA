import logging
from typing import Dict, List, Optional

from reflection.models import ReflectionReport

logger = logging.getLogger("AURA.Reflection.History")


class ReflectionHistoryStore:
    def __init__(self):
        self._reports: Dict[str, ReflectionReport] = {}

    def save_report(self, report: ReflectionReport) -> None:
        self._reports[report.report_id] = report

    def get_report(self, report_id: str) -> Optional[ReflectionReport]:
        return self._reports.get(report_id)

    def list_reports(self) -> List[ReflectionReport]:
        return list(self._reports.values())
