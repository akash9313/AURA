import logging
from typing import Any, Dict

logger = logging.getLogger("AURA.API.Telemetry")


class APITelemetryRecorder:
    """Tracks API metrics: latency, error rates, request counts, and endpoint hit frequencies."""

    def __init__(self):
        self.total_requests: int = 0
        self.total_errors: int = 0

    def record_request(self, endpoint: str, status_code: int, duration_ms: float) -> None:
        self.total_requests += 1
        if status_code >= 400:
            self.total_errors += 1
        logger.info(f"API Call [{endpoint}] -> {status_code} ({duration_ms:.2f}ms)")

    def get_stats(self) -> Dict[str, Any]:
        error_rate = (self.total_errors / float(self.total_requests)) * 100.0 if self.total_requests > 0 else 0.0

        return {
            "total_requests": self.total_requests,
            "total_errors": self.total_errors,
            "error_rate_percent": round(error_rate, 2),
        }
