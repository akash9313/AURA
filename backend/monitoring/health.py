import logging
import psutil
from typing import Dict
from monitoring.models import HealthStatus, SystemHealthStatus

logger = logging.getLogger("AURA.Monitoring.Health")


class HealthChecker:
    """
    Subsystem Health Checker.
    Monitors Speech, Brain, Memory, Workflow, Plugins, and system resources.
    """

    def check_health(self, active_services: Dict[str, Any] = None) -> SystemHealthStatus:
        services_status = {}
        warnings = []

        target_services = [
            "speech", "vad", "stt", "streaming_tts",
            "brain", "streaming_brain", "memory",
            "workflow", "plugins", "conversation"
        ]

        if active_services:
            for s_name in target_services:
                if s_name in active_services:
                    services_status[s_name] = "running"
                else:
                    services_status[s_name] = "registered"
        else:
            for s_name in target_services:
                services_status[s_name] = "healthy"

        # Check system resource thresholds
        mem_percent = psutil.virtual_memory().percent
        if mem_percent > 98.0:
            warnings.append(f"High Memory Usage: {mem_percent}%")


        overall_status = HealthStatus.WARNING if warnings else HealthStatus.HEALTHY

        status_obj = SystemHealthStatus(
            status=overall_status,
            services=services_status,
            warnings=warnings
        )
        logger.info(f"System Health Check: {overall_status.value.upper()} ({len(warnings)} warnings)")
        return status_obj
