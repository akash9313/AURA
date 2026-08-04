"""
Failure Diagnostics Engine.
Classifies raw exceptions and browser errors into FailureType, analyzes root causes, and generates DiagnosticReports.
"""

import logging
import re
import time
from typing import List, Optional

from browser.recovery.models import DiagnosticReport, FailureType, RecoveryStrategy

logger = logging.getLogger("AURA.Browser.Recovery.Diagnostics")


class DiagnosticEngine:
    """
    Analyzes browser failures and produces structured diagnostic reports and repair recommendations.
    """

    def analyze_failure(self, error: Exception, context: Optional[str] = None) -> FailureType:
        """
        Classify raw Exception into a structured FailureType.

        Args:
            error: Raw Exception object or error string.
            context: Additional context string.

        Returns:
            FailureType enum value.
        """
        err_msg = str(error).lower()
        ctx_msg = (context or "").lower()
        full_msg = f"{err_msg} {ctx_msg}"

        if "dns" in full_msg or "name_not_resolved" in full_msg or "getaddrinfo failed" in full_msg:
            return FailureType.DNS_FAILURE
        if "ssl" in full_msg or "cert" in full_msg or "certificate" in full_msg:
            return FailureType.SSL_FAILURE
        if "timeout" in full_msg or "timed out" in full_msg:
            return FailureType.NAVIGATION_TIMEOUT
        if "browser" in full_msg and ("closed" in full_msg or "crash" in full_msg or "disconnect" in full_msg):
            return FailureType.BROWSER_CRASH
        if "target closed" in full_msg or "page closed" in full_msg or "page crashed" in full_msg:
            return FailureType.PAGE_CRASH
        if "detached" in full_msg or "frame was detached" in full_msg:
            return FailureType.ELEMENT_DETACHED
        if "element not found" in full_msg or "not locate" in full_msg:
            return FailureType.ELEMENT_MISSING
        if "session" in full_msg and ("expired" in full_msg or "lost" in full_msg or "invalid" in full_msg):
            return FailureType.SESSION_LOST
        if "download" in full_msg:
            return FailureType.DOWNLOAD_FAILURE
        if "upload" in full_msg:
            return FailureType.UPLOAD_FAILURE
        if "offline" in full_msg or "net::err_internet_disconnected" in full_msg:
            return FailureType.NETWORK_OFFLINE

        return FailureType.UNKNOWN

    def generate_report(
        self,
        error: Exception,
        failure_type: FailureType,
        strategy: Optional[RecoveryStrategy] = None,
        success: bool = False,
        duration_ms: float = 0.0,
    ) -> DiagnosticReport:
        """
        Build a structured DiagnosticReport object with actionable recommendations.
        """
        root_cause = f"{type(error).__name__}: {str(error)}"
        recommendations = self._generate_recommendations(failure_type, strategy)

        report = DiagnosticReport(
            failure_type=failure_type,
            root_cause=root_cause,
            recovery_attempted=strategy is not None,
            recovery_strategy=strategy,
            success=success,
            duration_ms=duration_ms,
            recommendations=recommendations,
        )

        logger.info(
            f"Generated DiagnosticReport '{report.report_id}' for '{failure_type.value}' "
            f"(Strategy: {strategy.value if strategy else 'None'}, Success: {success})"
        )
        return report

    def _generate_recommendations(self, failure_type: FailureType, strategy: Optional[RecoveryStrategy]) -> List[str]:
        recs = []
        if failure_type == FailureType.NAVIGATION_TIMEOUT:
            recs.append("Increase navigation timeout or switch to DOM_READY wait strategy.")
            recs.append("Refresh page and clear transient network requests.")
        elif failure_type == FailureType.BROWSER_CRASH:
            recs.append("Recycle Playwright Chromium process.")
            recs.append("Restore page state from latest StateSnapshot.")
        elif failure_type == FailureType.ELEMENT_MISSING:
            recs.append("Use Fallback Locator strategy (fuzzy text or ARIA role).")
            recs.append("Verify if DOM dynamic rendering completed.")
        elif failure_type == FailureType.SESSION_LOST:
            recs.append("Restore authentication cookies from Session Store.")

        if not recs:
            recs.append("Retry action with exponential backoff delay.")

        return recs
