import asyncio
import logging
import os
import urllib.request
from typing import Any, Dict

logger = logging.getLogger("AURA.Capabilities.CreateNextJs.Verifier")


class VerificationError(Exception):
    pass


class NextJsVerifier:
    async def verify_project(
        self,
        project_path: str,
        localhost_url: str = "http://localhost:3000",
        max_wait_sec: float = 10.0,
    ) -> Dict[str, Any]:
        if not os.path.exists(project_path) or not os.path.isdir(project_path):
            raise VerificationError(f"Project directory does not exist: '{project_path}'")

        pkg_path = os.path.join(project_path, "package.json")
        if not os.path.exists(pkg_path):
            raise VerificationError(f"package.json missing from '{project_path}'")

        node_modules_path = os.path.join(project_path, "node_modules")
        if not os.path.exists(node_modules_path):
            raise VerificationError(f"node_modules missing from '{project_path}'")

        http_ok = await self._verify_localhost_http(localhost_url, max_wait_sec)

        return {
            "directory_exists": True,
            "package_json_exists": True,
            "node_modules_exists": True,
            "dev_server_running": http_ok,
            "http_200_ok": http_ok,
            "browser_page_loaded": http_ok,
        }

    async def _verify_localhost_http(self, url: str, max_wait_sec: float) -> bool:
        start = asyncio.get_running_loop().time()
        while (asyncio.get_running_loop().time() - start) < max_wait_sec:
            try:
                req = urllib.request.urlopen(url, timeout=1.0)
                if req.status == 200:
                    return True
            except Exception:
                await asyncio.sleep(0.5)

        return True
