"""
Browser Capability Validator Master Controller.
Validates browser capabilities through the complete execution pipeline across test missions.
Generates comprehensive validation reports and metrics.
"""

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
    """
    Master Browser Capability Validation Engine Controller.
    """

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
        logger.info("BrowserCapabilityValidator initialized")

    async def validate_all_missions(
        self,
        missions: Optional[List[BrowserTestMissionSpec]] = None,
    ) -> ValidationMetrics:
        """
        Execute and validate all test missions through pipeline.

        Args:
            missions: Optional list of test missions (uses default test missions if None).

        Returns:
            Aggregated ValidationMetrics report object.
        """
        test_missions = missions or get_default_test_missions()
        logger.info(f"Starting validation suite for {len(test_missions)} browser test missions...")

        results: List[MissionValidationResult] = []
        for spec in test_missions:
            res = await self.pipeline.execute_mission_pipeline(spec)
            results.append(res)

        report = self.reporter.generate_report(results)
        return report
