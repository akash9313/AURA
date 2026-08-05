"""
System Validation & Quality Assurance Domain Models.
Defines SystemBenchmarkResult, ScenarioValidationResult, RecoveryValidationResult, and FullSystemHealthSummary.
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ValidationStatus(Enum):
    """Validation test outcome status."""
    PASSED = "passed"
    FAILED = "failed"
    RECOVERED = "recovered"
    SKIPPED = "skipped"


@dataclass
class SystemBenchmarkResult:
    """Latency and resource usage benchmarks across AURA subsystems."""
    startup_time_ms: float = 0.0
    wakeword_latency_ms: float = 0.0
    stt_latency_ms: float = 0.0
    planning_latency_ms: float = 0.0
    execution_latency_ms: float = 0.0
    mission_duration_sec: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_pct: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "startup_time_ms": round(self.startup_time_ms, 2),
            "wakeword_latency_ms": round(self.wakeword_latency_ms, 2),
            "stt_latency_ms": round(self.stt_latency_ms, 2),
            "planning_latency_ms": round(self.planning_latency_ms, 2),
            "execution_latency_ms": round(self.execution_latency_ms, 2),
            "mission_duration_sec": round(self.mission_duration_sec, 3),
            "memory_usage_mb": round(self.memory_usage_mb, 2),
            "cpu_usage_pct": round(self.cpu_usage_pct, 2),
        }


@dataclass
class ScenarioValidationResult:
    """Result of an end-to-end user mission scenario validation."""
    scenario_id: str
    name: str
    status: ValidationStatus = ValidationStatus.PASSED
    duration_sec: float = 0.0
    steps_executed: int = 0
    evidence: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "name": self.name,
            "status": self.status.value,
            "duration_sec": round(self.duration_sec, 3),
            "steps_executed": self.steps_executed,
            "evidence": self.evidence,
            "error": self.error,
        }


@dataclass
class RecoveryValidationResult:
    """Result of a system fault injection and recovery strategy validation."""
    fault_type: str
    recovery_strategy: str
    status: ValidationStatus = ValidationStatus.PASSED
    recovery_time_sec: float = 0.0
    verified: bool = True
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fault_type": self.fault_type,
            "recovery_strategy": self.recovery_strategy,
            "status": self.status.value,
            "recovery_time_sec": round(self.recovery_time_sec, 3),
            "verified": self.verified,
            "error": self.error,
        }


@dataclass
class FullSystemHealthSummary:
    """Master System Health & Reliability Report summary."""
    total_scenarios: int = 0
    passed_scenarios: int = 0
    failed_scenarios: int = 0
    overall_success_rate: float = 0.0
    avg_duration_sec: float = 0.0
    recovery_success_rate: float = 0.0
    benchmarks: SystemBenchmarkResult = field(default_factory=SystemBenchmarkResult)
    scenario_results: List[ScenarioValidationResult] = field(default_factory=list)
    recovery_results: List[RecoveryValidationResult] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_scenarios": self.total_scenarios,
            "passed_scenarios": self.passed_scenarios,
            "failed_scenarios": self.failed_scenarios,
            "overall_success_rate": round(self.overall_success_rate, 2),
            "avg_duration_sec": round(self.avg_duration_sec, 3),
            "recovery_success_rate": round(self.recovery_success_rate, 2),
            "benchmarks": self.benchmarks.to_dict(),
            "scenario_results": [s.to_dict() for s in self.scenario_results],
            "recovery_results": [r.to_dict() for r in self.recovery_results],
            "timestamp": self.timestamp,
        }
