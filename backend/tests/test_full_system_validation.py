"""
Full AURA System QA, Reliability, Recovery, Stress, and Performance Validation Test Suite.
Tests SystemValidationSuiteRunner, SystemScenarioRunner, SystemRecoveryTestRunner, SystemPerformanceBenchmarkEngine, and SystemStressTestRunner.
"""

import asyncio
import sys
import unittest

sys.path.insert(0, ".")

from tests.system.models import (
    FullSystemHealthSummary,
    ValidationStatus,
)
from tests.system.scenarios import SystemScenarioRunner
from tests.system.recovery_tests import SystemRecoveryTestRunner
from tests.system.performance import SystemPerformanceBenchmarkEngine
from tests.system.stress_tests import SystemStressTestRunner
from tests.system.runner import SystemValidationSuiteRunner


class TestFullSystemValidation(unittest.TestCase):
    """Test suite for full AURA AI Operating System QA & Reliability validation."""

    def setUp(self):
        self.runner = SystemValidationSuiteRunner()

    def test_end_to_end_user_missions(self):
        """Test all 5 required end-to-end user mission scenarios."""
        scenario_runner = SystemScenarioRunner()
        results = asyncio.run(scenario_runner.run_all_scenarios())

        self.assertEqual(len(results), 5)
        for r in results:
            self.assertEqual(r.status, ValidationStatus.PASSED)
            self.assertGreater(r.steps_executed, 0)
            self.assertTrue(r.evidence.get("verified", False))

    def test_fault_injection_and_recovery(self):
        """Test system recovery across all 6 fault injection scenarios."""
        recovery_runner = SystemRecoveryTestRunner()
        results = asyncio.run(recovery_runner.run_all_recovery_tests())

        self.assertEqual(len(results), 6)
        for r in results:
            self.assertIn(r.status, (ValidationStatus.PASSED, ValidationStatus.RECOVERED))
            self.assertTrue(r.verified)

    def test_performance_benchmarks(self):
        """Test performance benchmark measurements for latency, CPU, and RAM."""
        benchmark_engine = SystemPerformanceBenchmarkEngine()
        bench = asyncio.run(benchmark_engine.measure_benchmarks())

        self.assertGreater(bench.startup_time_ms, 0.0)
        self.assertGreater(bench.wakeword_latency_ms, 0.0)
        self.assertGreater(bench.stt_latency_ms, 0.0)
        self.assertGreater(bench.planning_latency_ms, 0.0)
        self.assertGreater(bench.execution_latency_ms, 0.0)
        self.assertGreater(bench.memory_usage_mb, 0.0)

    def test_system_stress_suite(self):
        """Test system endurance across 100 sequential missions, repeated wake word, and browser sessions."""
        stress_runner = SystemStressTestRunner()
        res = asyncio.run(stress_runner.run_all_stress_tests())

        self.assertEqual(res["overall_status"], "PASSED")
        self.assertEqual(res["sequential_100"]["passed"], 100)
        self.assertEqual(res["wake_word"]["passed"], 50)
        self.assertEqual(res["browser_sessions"]["passed"], 10)

    def test_full_system_validation_runner(self):
        """Test full SystemValidationSuiteRunner executing scenario, recovery, benchmark, and stress suites."""
        summary: FullSystemHealthSummary = asyncio.run(self.runner.execute_full_validation_suite())

        self.assertEqual(summary.total_scenarios, 5)
        self.assertEqual(summary.passed_scenarios, 5)
        self.assertEqual(summary.overall_success_rate, 100.0)
        self.assertEqual(summary.recovery_success_rate, 100.0)


if __name__ == "__main__":
    unittest.main()
