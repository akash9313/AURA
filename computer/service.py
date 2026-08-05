import logging
from typing import Any, Dict, List, Optional

from core.service import Service
from computer.configuration import ComputerConfig
from computer.events import ComputerEvent
from computer.manager import ComputerManager
from computer.models import (
    ClipboardContent,
    ComputerHealthStatus,
    ComputerResult,
    ComputerState,
    DesktopWindowInfo,
)

logger = logging.getLogger("AURA.Computer.Service")


class ComputerService(Service):
    """
    Central Computer Service for AURA Desktop Automation.
    Dependency injection and provider management handled internally.
    """

    def __init__(self, bus: Any = None, config: Optional[ComputerConfig] = None):
        super().__init__(bus)
        self.config = config or ComputerConfig()
        self.manager = ComputerManager(bus=bus, config=self.config)
        logger.info("ComputerService initialized")

    def start(self) -> None:
        """Start Computer Service and load desktop automation provider."""
        logger.info("Starting ComputerService...")
        self._publish_event(ComputerEvent.COMPUTER_STARTED, {})

        try:
            self.manager.initialize_provider()
            self._publish_event(ComputerEvent.COMPUTER_READY, {"provider": self.manager.provider.get_provider_name()})
            logger.info("ComputerService is READY")
        except Exception as e:
            logger.error(f"Failed to start ComputerService: {e}")
            raise

    def stop(self) -> None:
        """Stop Computer Service."""
        logger.info("Stopping ComputerService...")
        self.manager.state = ComputerState.STOPPED
        self._publish_event(ComputerEvent.COMPUTER_STOPPED, {})
        logger.info("ComputerService STOPPED")

    def is_healthy(self) -> bool:
        """Audit health of Computer Service."""
        return self.manager.state == ComputerState.READY

    async def launch_app(self, app_name: str, args: Optional[List[str]] = None) -> ComputerResult:
        """Launch a desktop application."""
        self._ensure_ready()
        res = await self.manager.provider.launch_app(app_name, args)
        self._track_result(res)
        return res

    async def terminate_app(self, target: Any) -> ComputerResult:
        """Terminate a desktop process."""
        self._ensure_ready()
        res = await self.manager.provider.terminate_app(target)
        self._track_result(res)
        return res

    async def get_active_window(self) -> Optional[DesktopWindowInfo]:
        """Get active foreground window details."""
        self._ensure_ready()
        return await self.manager.provider.get_active_window()

    async def list_windows(self) -> List[DesktopWindowInfo]:
        """List active desktop windows."""
        self._ensure_ready()
        return await self.manager.provider.list_windows()

    async def focus_window(self, target: Any) -> ComputerResult:
        """Focus target window."""
        self._ensure_ready()
        res = await self.manager.provider.focus_window(target)
        self._track_result(res)
        return res

    async def click(self, x: int, y: int, button: str = "left", double: bool = False) -> ComputerResult:
        """Click screen coordinates."""
        self._ensure_ready()
        res = await self.manager.provider.mouse_click(x, y, button=button, double=double)
        self._track_result(res)
        return res

    async def type_text(self, text: str, target: Optional[Any] = None) -> ComputerResult:
        """Type text into focused element or window."""
        self._ensure_ready()
        res = await self.manager.provider.type_text(text, target=target)
        self._track_result(res)
        return res

    async def read_clipboard(self) -> ClipboardContent:
        """Read clipboard content."""
        self._ensure_ready()
        return await self.manager.provider.read_clipboard()

    async def write_clipboard(self, text: str) -> ComputerResult:
        """Write text payload to clipboard."""
        self._ensure_ready()
        res = await self.manager.provider.write_clipboard(text)
        self._track_result(res)
        return res

    async def open_folder(self, folder_path: str) -> ComputerResult:
        """Open folder in File Explorer."""
        self._ensure_ready()
        res = await self.manager.provider.open_folder(folder_path)
        self._track_result(res)
        return res

    def get_health_status(self) -> ComputerHealthStatus:
        """Get subsystem health telemetry status."""
        return self.manager.get_health_status()

    def _ensure_ready(self) -> None:
        if not self.manager.provider:
            self.start()

    def _track_result(self, res: ComputerResult) -> None:
        self.manager.total_actions += 1
        if res.success:
            self.manager.successful_actions += 1
        else:
            self.manager.failed_actions += 1
            self.manager.last_error = res.message

    def _publish_event(self, event: ComputerEvent, data: Dict[str, Any]) -> None:
        if self.bus:
            try:
                self.bus.publish(event.value, data)
            except Exception as e:
                logger.error(f"Failed to publish event '{event.value}': {e}")


# Backwards compatibility alias
ComputerUseService = ComputerService
