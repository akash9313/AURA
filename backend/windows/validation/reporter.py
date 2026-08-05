"""
Desktop Validation Reporter.
Generates structured metrics and report summaries:
- Execution timeline
- Verification evidence
- Recovery attempts
- Mission duration
- Success metrics
"""

import logging
from typing import List

from windows.validation.models import (
    DesktopMissionResult,
    DesktopValidationMetrics,
)

logger = logging.getLogger("AURA.Windows.Validation.Reporter")


class DesktopValidationReporter:
    """
    Summarizes mission validation outcomes into DesktopValidationMetrics reports.
    """

    def generate_report(self, results: List[DesktopMissionResult]) -> DesktopValidationMetrics:
        """
        Generate aggregated DesktopValidationMetrics report from mission validation results.

        Args:
            results: List of DesktopMissionResult items.

        Returns:
            DesktopValidationMetrics object.
        """
        total = len(results)
        passed = sum(1 for r in results if r.status.value in ("passed", "recovered"))
        failed = total - passed
        overall_rate = (passed / total * 100.0) if total > 0 else 0.0
        total_duration = sum(r.total_duration_sec for r in results)
        avg_duration = (total_duration / total) if total > 0 else 0.0
        total_recoveries = sum(r.recovery_attempts for r in results)

        metrics = DesktopValidationMetrics(
            total_missions=total,
            passed_missions=passed,
            failed_missions=failed,
            overall_success_rate=overall_rate,
            total_duration_sec=total_duration,
            avg_mission_duration_sec=avg_duration,
            total_recovery_attempts=total_recoveries,
        )

        logger.info(f"Desktop Validation Report Generated: {passed}/{total} missions passed ({overall_rate:.1f}% success rate) with {total_recoveries} recovery attempts.")
        return metrics
