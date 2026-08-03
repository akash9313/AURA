import logging
from typing import Any, Dict, List, Union
from PIL import Image
from vision.image_utils import load_image

logger = logging.getLogger("AURA.Vision.Barcode")


class BarcodeDetector:
    """
    Detector for reading 1D barcodes and 2D QR codes.
    """

    def detect_barcodes(self, image_source: Union[str, bytes, Image.Image]) -> List[Dict[str, Any]]:
        """
        Scan image for QR codes and barcodes.

        Returns:
            List[dict]: Decoded barcode entries with type and content payload.
        """
        image = load_image(image_source)
        results: List[Dict[str, Any]] = []

        # 1. Try PyZBar if available
        try:
            from pyzbar.pyzbar import decode
            decoded = decode(image)
            for item in decoded:
                results.append({
                    "type": item.type,
                    "data": item.data.decode("utf-8"),
                    "rect": {
                        "x": item.rect.left,
                        "y": item.rect.top,
                        "width": item.rect.width,
                        "height": item.rect.height
                    }
                })
            if results:
                logger.info(f"Decoded {len(results)} barcode/QR code(s) via PyZBar.")
                return results
        except Exception as e:
            logger.debug(f"PyZBar barcode scanner unavailable: {e}.")

        return results
