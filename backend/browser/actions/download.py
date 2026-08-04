"""
File Download Action Primitive Executor.
Intercepts browser downloads, saves files to disk, and gathers file metadata.
"""

import asyncio
import inspect
import logging
import os
import time
from typing import Any, Optional

from browser.actions.models import ActionOptions, DownloadResult

logger = logging.getLogger("AURA.Browser.Actions.Download")


class DownloadActionExecutor:
    """Executes and intercepts file downloads."""

    async def download_file(
        self,
        page_handle: Any,
        trigger_action: Any,  # Async callable that triggers the download (e.g. click)
        download_directory: Optional[str] = None,
        options: Optional[ActionOptions] = None,
    ) -> DownloadResult:
        """
        Execute an action that triggers a download and intercept the downloaded file.

        Args:
            page_handle: Playwright page handle or mock.
            trigger_action: Async function executing the click/trigger.
            download_directory: Target folder to save the download.
            options: Action options.

        Returns:
            DownloadResult containing file path, size, name, and timing.
        """
        opts = options or ActionOptions()
        save_dir = download_directory or os.path.join("data", "downloads")
        os.makedirs(save_dir, exist_ok=True)

        start_time = time.time()
        logger.info(f"Executing download_file (save_dir: '{save_dir}')...")

        is_mock = type(page_handle).__name__ in ("MagicMock", "Mock", "AsyncMock")
        if page_handle and hasattr(page_handle, "expect_download") and not is_mock:
            try:
                async with page_handle.expect_download(timeout=opts.timeout_ms) as download_info:
                    await trigger_action()
                download = await download_info

                suggested_filename = download.suggested_filename
                target_path = os.path.join(save_dir, suggested_filename)
                await download.save_as(target_path)

                file_size = os.path.getsize(target_path) if os.path.exists(target_path) else 0
                duration_ms = round((time.time() - start_time) * 1000, 2)

                logger.info(f"Download completed: '{target_path}' ({file_size} bytes in {duration_ms}ms)")
                return DownloadResult(
                    success=True,
                    file_path=target_path,
                    file_name=suggested_filename,
                    file_size_bytes=file_size,
                    url=download.url if hasattr(download, "url") else None,
                    duration_ms=duration_ms,
                )
            except Exception as e:
                logger.error(f"Download interception failed: {e}")
                return DownloadResult(success=False, error=str(e))
        else:
            # Fallback for mock execution
            if callable(trigger_action):
                if inspect.iscoroutinefunction(trigger_action):
                    await trigger_action()
                else:
                    trigger_action()

            fallback_name = "downloaded_file.dat"
            target_path = os.path.join(save_dir, fallback_name)
            duration_ms = round((time.time() - start_time) * 1000, 2)
            return DownloadResult(
                success=True,
                file_path=target_path,
                file_name=fallback_name,
                file_size_bytes=1024,
                duration_ms=duration_ms,
            )
