import logging
from typing import Any, List, Optional

from core.service import Service
from reflection.analyzer import ReflectionAnalyzer
from reflection.configuration import ReflectionConfig
from reflection.models import ReflectionReport

logger = logging.getLogger("AURA.Reflection.Service")


class ReflectionEngineService(Service):
    def __init__(
        self,
        bus: Any = None,
        config: Optional[ReflectionConfig] = None,
    ):
        super().__init__(bus)
        self.config = config or ReflectionConfig()
        self.analyzer = ReflectionAnalyzer(bus=bus, config=self.config)

    def analyze_workflow(self, workflow_result: Any) -> ReflectionReport:
        return self.analyzer.analyze_workflow(workflow_result)

    def get_reflection_report(self, report_id: str) -> Optional[ReflectionReport]:
        return self.analyzer.history_store.get_report(report_id)

    def list_reflection_reports(self) -> List[ReflectionReport]:
        return self.analyzer.history_store.list_reports()

    def start(self) -> None:
        logger.info("Starting ReflectionEngineService...")

    def stop(self) -> None:
        logger.info("Stopping ReflectionEngineService...")

    def is_healthy(self) -> bool:
        return True
