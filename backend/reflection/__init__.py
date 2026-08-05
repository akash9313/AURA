"""
AURA Reflection Engine Subsystem (`backend/reflection/`).
Evaluates completed workflows and generates actionable recommendations for future executions without modifying code directly.
"""

from reflection.analyzer import ReflectionAnalyzer
from reflection.configuration import ReflectionConfig
from reflection.evaluator import WorkflowEvaluator
from reflection.events import ReflectionEvent
from reflection.history import ReflectionHistoryStore
from reflection.metrics import MetricsCollector
from reflection.models import (
    PatternInsight,
    Recommendation,
    RecommendationType,
    ReflectionReport,
    TaskMetric,
)
from reflection.patterns import PatternDetector
from reflection.recommendations import RecommendationEngine
from reflection.service import ReflectionEngineService

__all__ = [
    "ReflectionEngineService",
    "ReflectionAnalyzer",
    "WorkflowEvaluator",
    "PatternDetector",
    "RecommendationEngine",
    "MetricsCollector",
    "ReflectionHistoryStore",
    "ReflectionConfig",
    "Recommendation",
    "RecommendationType",
    "PatternInsight",
    "TaskMetric",
    "ReflectionReport",
    "ReflectionEvent",
]
