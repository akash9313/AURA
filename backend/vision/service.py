import logging
from core.events import Event
from core.service import Service
from vision.manager import VisionManager

logger = logging.getLogger("AURA.VisionService")


class VisionService(Service):
    """
    VisionService integrates VisionManager capabilities into the AURA EventBus.
    """

    def __init__(self, bus, manager: VisionManager = None):
        super().__init__(bus)
        self.manager = manager if manager is not None else VisionManager()

    def start(self) -> None:
        logger.info("Vision Service Started")

        self.bus.subscribe(Event.SCREEN_CAPTURE_REQUEST, self.on_screen_capture_request)
        self.bus.subscribe(Event.CAMERA_CAPTURE_REQUEST, self.on_camera_capture_request)
        self.bus.subscribe(Event.IMAGE_ANALYZE_REQUEST, self.on_image_analyze_request)
        self.bus.subscribe(Event.DOCUMENT_ANALYZE_REQUEST, self.on_document_analyze_request)

    def stop(self) -> None:
        logger.info("Vision Service Stopped")

    def on_screen_capture_request(self, data: dict = None) -> None:
        region = data.get("region") if isinstance(data, dict) else None
        filepath = self.manager.capture_screen(region=region)
        logger.info(f"Captured screen image: '{filepath}'")
        self.bus.publish(Event.SCREEN_CAPTURED, {"filepath": filepath})

    def on_camera_capture_request(self, data: dict = None) -> None:
        dev_id = data.get("device_id", 0) if isinstance(data, dict) else 0
        filepath = self.manager.capture_camera(device_id=dev_id)
        logger.info(f"Captured camera image: '{filepath}'")
        self.bus.publish(Event.IMAGE_CAPTURED, {"filepath": filepath})

    def on_image_analyze_request(self, data: dict) -> None:
        if not isinstance(data, dict):
            return
        source = data.get("source") or data.get("filepath")
        prompt = data.get("prompt", "Describe this image in detail.")
        if source:
            result = self.manager.analyze_image(source, prompt=prompt)
            self.bus.publish(Event.VISION_COMPLETED, result.to_dict())

    def on_document_analyze_request(self, data: dict) -> None:
        if not isinstance(data, dict):
            return
        source = data.get("source") or data.get("filepath")
        if source:
            result = self.manager.read_pdf_page(source)
            self.bus.publish(Event.DOCUMENT_ANALYZED, result.to_dict())
