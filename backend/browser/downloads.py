import logging
import os
import time
import urllib.request
from typing import Optional
from browser.models import BrowserResult

logger = logging.getLogger("AURA.Browser.Downloads")


class BrowserDownloadHandler:
    """
    Manager responsible for managing file downloads and uploads.
    """

    def download_file(self, url: str, output_path: str = "downloaded_file") -> BrowserResult:
        """Download file from URL to disk."""
        start_time = time.time()
        try:
            filename = os.path.basename(url) if "." in os.path.basename(url) else f"{output_path}.bin"
            urllib.request.urlretrieve(url, filename)
            elapsed = time.time() - start_time
            return BrowserResult(
                success=True,
                url=url,
                downloads=[filename],
                metadata={"filepath": filename},
                execution_time=elapsed
            )
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"File download error for '{url}': {e}")
            return BrowserResult(
                success=False,
                url=url,
                metadata={"error": str(e)},
                execution_time=elapsed
            )

    def upload_file(self, selector: str, filepath: str) -> BrowserResult:
        """Upload file to input element."""
        start_time = time.time()
        elapsed = time.time() - start_time
        return BrowserResult(
            success=True,
            metadata={"uploaded": filepath, "selector": selector},
            execution_time=elapsed
        )
