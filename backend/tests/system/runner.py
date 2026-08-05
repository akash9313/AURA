"""
System Validation Suite Master Controller.
Coordinates scenario execution, recovery tests, performance benchmarks, and stress tests.
"""

import asyncio
import logging
from typing import Any, Dict, Optional

from tests.system.models import FullSystemHealthSummary
from tests.system.performance import SystemPerformanceBenchmarkEngine
from tests.system.recovery_tests import SystemRecoveryTestRunner
from tests.system.reporter import FullSystemValidationReporter
from tests.system.scenarios import SystemScenarioRunner
from tests.system.stress_tests import SystemStressTestRunner

logger = logging.getLogger("AURA.SystemValidation.Runner")


class SystemValidationSuiteRunner:
    """
    Master QA & Validation Suite controller executing end-to-end user mission benchmarks.
    """

    def __init__(self, kernel_services: Optional[Dict[str, Any]] = None):
        self.scenario_runner = SystemScenarioRunner(kernel_services)
        self.recovery_runner = SystemRecoveryTestRunner()
        self.benchmark_engine = SystemPerformanceBenchmarkEngine()
        self.stress_runner = SystemStressTestRunner()
        self.reporter = FullSystemValidationReporter()

    async def execute_full_validation_suite(self) -> FullSystemHealthSummary:
        """
        Execute full end-to-end validation suite across scenarios, recovery, benchmarks, and stress.

        Returns:
            FullSystemHealthSummary report.
        """
        logger.info("Starting Complete AURA System Validation Suite Execution...")

        scenarios = await self.scenario_runner.run_all_scenarios()
        recovery = await self.recovery_runner.run_all_recovery_tests()
        benchmarks = await self.benchmark_engine.measure_benchmarks()
        _ = await self.stress_runner.run_all_stress_tests()

        summary = self.reporter.generate_health_summary(scenarios, recovery, benchmarks)
        return summary
