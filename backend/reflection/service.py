"""
Reflection Engine Service.
Top-level AURA service integrating the Reflection Engine into the kernel framework.
Evaluates completed workflows and generates actionable recommendations without modifying workflows directly.
"""

import logging
from typing import Any, List, Optional

from core.service import Service
from reflection.analyzer import ReflectionAnalyzer
from reflection.configuration import ReflectionConfig
from reflection.models import ReflectionReport

logger = logging.getLogger("AURA.Reflection.Service")


class ReflectionEngineService(Service):
    """
    Service wrapper exposing Reflection Engine capabilities to AURA Runtime.
    """

    def __init__(
        self,
        bus: Any = None,
        config: Optional[ReflectionConfig] = None,
    ):
        super().__init__(bus)
        self.config = config or ReflectionConfig()
        self.analyzer = ReflectionAnalyzer(bus=bus, config=self.config)
        logger.info("ReflectionEngineService initialized")

    def analyze_workflow(self, workflow_result: Any) -> ReflectionReport:
        """
        Analyze completed workflow execution and return ReflectionReport.

        Returns:
            ReflectionReport object.
        """
        return self.analyzer.analyze_workflow(workflow_result)

    def get_reflection_report(self, report_id: str) -> Optional[ReflectionReport]:
        """Retrieve historical reflection report by ID."""
        return self.analyzer.history_store.get_report(report_id)

    def list_reflection_reports(self) -> List[ReflectionReport]:
        """List all historical reflection reports."""
        return self.analyzer.history_store.list_reports()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        logger.info("Starting ReflectionEngineService...")

    def stop(self) -> None:
        logger.info("Stopping ReflectionEngineService...")

    def is_healthy(self) -> bool:
        return True
