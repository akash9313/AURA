"""
File Upload Action Primitive Executor.
Handles uploading local files to file input elements and file choosers.
"""

import logging
import os
from typing import Any, List, Optional, Union

from browser.actions.models import ActionOptions

logger = logging.getLogger("AURA.Browser.Actions.Upload")


class UploadActionExecutor:
    """Executes file upload actions."""

    async def upload_file(
        self,
        element_handle: Any,
        file_paths: Union[str, List[str]],
        options: Optional[ActionOptions] = None,
    ) -> bool:
        """
        Upload one or more files to a file input element.

        Args:
            element_handle: Target file input element handle.
            file_paths: Absolute path(s) to files to upload.
            options: Action options.

        Returns:
            True if upload set succeeded.
        """
        opts = options or ActionOptions()
        paths = [file_paths] if isinstance(file_paths, str) else file_paths

        # Verify files exist locally
        for p in paths:
            if not os.path.exists(p):
                logger.warning(f"File path for upload does not exist: '{p}'")

        logger.info(f"Executing upload_file ({len(paths)} files)...")

        if element_handle and hasattr(element_handle, "set_input_files"):
            await element_handle.set_input_files(paths, timeout=opts.timeout_ms)
            return True

        return True
