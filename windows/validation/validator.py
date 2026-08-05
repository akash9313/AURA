import asyncio
import logging
from typing import Any, List, Optional

from capabilities.service import CapabilityService
from verification.service import GoalVerificationService
from windows.service import WindowsService
from windows.validation.configuration import DesktopValidationConfig
from windows.validation.missions import DesktopTestMissionSpec, get_default_desktop_test_missions
from windows.validation.models import DesktopMissionResult, DesktopValidationMetrics
from windows.validation.pipeline import DesktopValidationPipeline
from windows.validation.reporter import DesktopValidationReporter

logger = logging.getLogger("AURA.Windows.Validation.Validator")


class DesktopCapabilityValidator:
    def __init__(
        self,
        bus: Any = None,
        config: Optional[DesktopValidationConfig] = None,
        capability_service: Optional[CapabilityService] = None,
        windows_service: Optional[WindowsService] = None,
        verification_service: Optional[GoalVerificationService] = None,
    ):
        self.bus = bus
        self.config = config or DesktopValidationConfig()
        self.pipeline = DesktopValidationPipeline(
            bus=bus,
            config=self.config,
            capability_service=capability_service,
            windows_service=windows_service,
            verification_service=verification_service,
        )
        self.reporter = DesktopValidationReporter()

    async def validate_all_missions(
        self,
        missions: Optional[List[DesktopTestMissionSpec]] = None,
    ) -> DesktopValidationMetrics:
        test_missions = missions or get_default_desktop_test_missions()
        results: List[DesktopMissionResult] = []
        for spec in test_missions:
            res = await self.pipeline.execute_mission_pipeline(spec)
            results.append(res)

        report = self.reporter.generate_report(results)
        return report
