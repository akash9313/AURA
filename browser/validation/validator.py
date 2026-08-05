import asyncio
import logging
from typing import Any, List, Optional

from browser.service import BrowserService
from browser.validation.configuration import BrowserValidationConfig
from browser.validation.missions import BrowserTestMissionSpec, get_default_test_missions
from browser.validation.models import MissionValidationResult, ValidationMetrics
from browser.validation.pipeline import ValidationPipeline
from browser.validation.reporter import ValidationReporter
from capabilities.service import CapabilityService
from verification.service import GoalVerificationService

logger = logging.getLogger("AURA.Browser.Validation.Validator")


class BrowserCapabilityValidator:
    def __init__(
        self,
        bus: Any = None,
        config: Optional[BrowserValidationConfig] = None,
        capability_service: Optional[CapabilityService] = None,
        browser_service: Optional[BrowserService] = None,
        verification_service: Optional[GoalVerificationService] = None,
    ):
        self.bus = bus
        self.config = config or BrowserValidationConfig()
        self.pipeline = ValidationPipeline(
            bus=bus,
            config=self.config,
            capability_service=capability_service,
            browser_service=browser_service,
            verification_service=verification_service,
        )
        self.reporter = ValidationReporter()

    async def validate_all_missions(
        self,
        missions: Optional[List[BrowserTestMissionSpec]] = None,
    ) -> ValidationMetrics:
        test_missions = missions or get_default_test_missions()
        results: List[MissionValidationResult] = []
        for spec in test_missions:
            res = await self.pipeline.execute_mission_pipeline(spec)
            results.append(res)

        report = self.reporter.generate_report(results)
        return report
