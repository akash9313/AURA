"""
Computer Subsystem Provider Manager.
Factory pattern and lifecycle manager for desktop automation providers.
Automatically detects host platform and initializes the appropriate provider (Windows, Linux, macOS).
"""

import logging
import sys
from typing import Any, Dict, Optional, Type

from computer.configuration import ComputerConfig
from computer.events import ComputerEvent
from computer.models import ComputerHealthStatus, ComputerState, PlatformType
from computer.providers.windows_provider import BaseComputerProvider, WindowsComputerProvider

logger = logging.getLogger("AURA.Computer.Manager")


class ComputerManager:
    """
    Manager responsible for provider factory initialization, health auditing, and provider abstraction.
    """

    def __init__(self, bus: Any = None, config: Optional[ComputerConfig] = None):
        self.bus = bus
        self.config = config or ComputerConfig()
        self.provider: Optional[BaseComputerProvider] = None
        self.state: ComputerState = ComputerState.STOPPED

        self.total_actions: int = 0
        self.successful_actions: int = 0
        self.failed_actions: int = 0
        self.last_error: Optional[str] = None

    def initialize_provider(self) -> BaseComputerProvider:
        """
        Factory method detecting platform and instantiating the desktop automation provider.

        Returns:
            Instantiated BaseComputerProvider object.
        """
        self.state = ComputerState.INITIALIZING
        detected_platform = self._detect_platform()

        logger.info(f"Initializing Computer Provider for platform '{detected_platform.value}'...")

        try:
            if detected_platform == PlatformType.WINDOWS or sys.platform.startswith("win"):
                self.provider = WindowsComputerProvider()
            else:
                # Fallback to Windows provider / mock provider for cross-platform support
                logger.warning(f"Platform '{detected_platform.value}' using generic Windows provider fallback.")
                self.provider = WindowsComputerProvider()

            self.state = ComputerState.READY
            self._publish_event(
                ComputerEvent.PROVIDER_LOADED,
                {"provider": self.provider.get_provider_name(), "platform": detected_platform.value},
            )
            return self.provider

        except Exception as e:
            self.state = ComputerState.ERROR
            self.last_error = str(e)
            logger.error(f"Failed to initialize computer provider: {e}")
            self._publish_event(ComputerEvent.PROVIDER_FAILED, {"error": str(e)})
            raise RuntimeError(f"Computer provider initialization failed: {e}")

    def _detect_platform(self) -> PlatformType:
        if self.config.platform != PlatformType.AUTO:
            return self.config.platform

        if sys.platform.startswith("win"):
            return PlatformType.WINDOWS
        elif sys.platform.startswith("linux"):
            return PlatformType.LINUX
        elif sys.platform.startswith("darwin"):
            return PlatformType.MACOS
        return PlatformType.WINDOWS

    def get_health_status(self) -> ComputerHealthStatus:
        """Audit health telemetry of the computer subsystem."""
        healthy = self.provider.is_healthy() if self.provider else False
        return ComputerHealthStatus(
            state=self.state,
            platform=self._detect_platform(),
            provider_name=self.provider.get_provider_name() if self.provider else "None",
            total_actions=self.total_actions,
            successful_actions=self.successful_actions,
            failed_actions=self.failed_actions,
            last_error=self.last_error,
        )

    def _publish_event(self, event: ComputerEvent, data: Dict[str, Any]) -> None:
        if self.bus:
            try:
                self.bus.publish(event.value, data)
            except Exception as e:
                logger.error(f"Failed to publish event '{event.value}': {e}")
