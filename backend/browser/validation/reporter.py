"""
Validation Reporter.
Generates structured metrics and report summaries:
- Mission duration
- Verification evidence
- Recovery attempts
- Success rate
"""

import logging
from typing import List

from browser.validation.models import (
    MissionValidationResult,
    ValidationMetrics,
)

logger = logging.getLogger("AURA.Browser.Validation.Reporter")


class ValidationReporter:
    """
    Summarizes mission validation outcomes into ValidationMetrics reports.
    """

    def generate_report(self, results: List[MissionValidationResult]) -> ValidationMetrics:
        """
        Generate aggregated ValidationMetrics report from mission validation results.

        Args:
            results: List of MissionValidationResult items.

        Returns:
            ValidationMetrics object.
        """
        total = len(results)
        passed = sum(1 for r in results if r.status.value in ("passed", "recovered"))
        failed = total - passed
        overall_rate = (passed / total * 100.0) if total > 0 else 0.0
        total_duration = sum(r.total_duration_sec for r in results)
        avg_duration = (total_duration / total) if total > 0 else 0.0
        total_recoveries = sum(r.recovery_attempts for r in results)

        metrics = ValidationMetrics(
            total_missions=total,
            passed_missions=passed,
            failed_missions=failed,
            overall_success_rate=overall_rate,
            total_duration_sec=total_duration,
            avg_mission_duration_sec=avg_duration,
            total_recovery_attempts=total_recoveries,
        )

        logger.info(f"Validation Report Generated: {passed}/{total} missions passed ({overall_rate:.1f}% success rate) with {total_recoveries} recovery attempts.")
        return metrics
