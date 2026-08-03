import base64
import io
import logging
import os
from typing import Tuple, Union
from PIL import Image, ImageDraw, ImageFont
from vision.models import BoundingBox

logger = logging.getLogger("AURA.Vision.ImageUtils")


def load_image(source: Union[str, bytes, Image.Image]) -> Image.Image:
    """
    Load an image from a file path, base64 string, raw bytes, or PIL Image.

    Args:
        source: Image source (filepath string, base64 string, bytes, or PIL Image).

    Returns:
        PIL.Image.Image: Loaded PIL RGB image.
    """
    if isinstance(source, Image.Image):
        return source.convert("RGB")

    if isinstance(source, bytes):
        return Image.open(io.BytesIO(source)).convert("RGB")

    if isinstance(source, str):
        # Check if base64 encoded string
        if source.startswith("data:image") or len(source) > 500:
            clean_b64 = source.split(",")[-1]
            raw_bytes = base64.b64decode(clean_b64)
            return Image.open(io.BytesIO(raw_bytes)).convert("RGB")

        # Assume file path
        if os.path.exists(source):
            return Image.open(source).convert("RGB")
        else:
            raise FileNotFoundError(f"Image file path not found: '{source}'")

    raise ValueError(f"Unsupported image source type: {type(source)}")


def image_to_base64(image: Image.Image, format: str = "PNG") -> str:
    """Convert a PIL Image to a base64 encoded string."""
    buffered = io.BytesIO()
    image.save(buffered, format=format)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def resize_image(image: Image.Image, max_dim: int = 1024) -> Image.Image:
    """Resize image maintaining aspect ratio so neither dimension exceeds max_dim."""
    w, h = image.size
    if w <= max_dim and h <= max_dim:
        return image

    if w > h:
        new_w = max_dim
        new_h = int(h * (max_dim / w))
    else:
        new_h = max_dim
        new_w = int(w * (max_dim / h))

    return image.resize((new_w, new_h), Image.Resampling.LANCZOS)


def crop_image(image: Image.Image, box: BoundingBox) -> Image.Image:
    """Crop image using a BoundingBox."""
    w, h = image.size
    left = max(0, min(box.x, w))
    top = max(0, min(box.y, h))
    right = max(left + 1, min(box.x + box.width, w))
    bottom = max(top + 1, min(box.y + box.height, h))
    return image.crop((left, top, right, bottom))


def create_fallback_image(text: str = "AURA Vision Capture", size: Tuple[int, int] = (800, 600)) -> Image.Image:
    """Create a synthetic PIL Image canvas with text for fallbacks."""
    img = Image.new("RGB", size, color=(30, 30, 45))
    draw = ImageDraw.Draw(img)
    draw.rectangle([10, 10, size[0] - 10, size[1] - 10], outline=(100, 150, 255), width=3)
    draw.text((30, size[1] // 2), f"📷 {text}", fill=(255, 255, 255))
    return img
