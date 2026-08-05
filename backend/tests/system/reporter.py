"""
System Health & Reliability Validation Reporter.
Generates comprehensive reports covering:
- Mission success rate
- Average duration
- Recovery statistics
- Failure causes
- Performance metrics
- System health summary
"""

import logging
from typing import List

from tests.system.models import (
    FullSystemHealthSummary,
    RecoveryValidationResult,
    ScenarioValidationResult,
    SystemBenchmarkResult,
)

logger = logging.getLogger("AURA.SystemValidation.Reporter")


class FullSystemValidationReporter:
    """
    Assembles FullSystemHealthSummary reports and generates Markdown summary text.
    """

    def generate_health_summary(
        self,
        scenario_results: List[ScenarioValidationResult],
        recovery_results: List[RecoveryValidationResult],
        benchmarks: SystemBenchmarkResult,
    ) -> FullSystemHealthSummary:
        """
        Generate FullSystemHealthSummary report object.

        Args:
            scenario_results: List of scenario outcomes.
            recovery_results: List of recovery outcomes.
            benchmarks: Latency & resource benchmark metrics.

        Returns:
            FullSystemHealthSummary object.
        """
        total = len(scenario_results)
        passed = sum(1 for s in scenario_results if s.status.value in ("passed", "recovered"))
        failed = total - passed
        overall_rate = (passed / total * 100.0) if total > 0 else 0.0
        avg_dur = sum(s.duration_sec for s in scenario_results) / float(total) if total > 0 else 0.0

        rec_passed = sum(1 for r in recovery_results if r.status.value in ("passed", "recovered"))
        rec_rate = (rec_passed / len(recovery_results) * 100.0) if recovery_results else 100.0

        summary = FullSystemHealthSummary(
            total_scenarios=total,
            passed_scenarios=passed,
            failed_scenarios=failed,
            overall_success_rate=overall_rate,
            avg_duration_sec=avg_dur,
            recovery_success_rate=rec_rate,
            benchmarks=benchmarks,
            scenario_results=scenario_results,
            recovery_results=recovery_results,
        )

        logger.info(f"Full System Health Summary: {passed}/{total} scenarios passed ({overall_rate:.1f}% success rate). Recovery rate: {rec_rate:.1f}%.")
        return summary
