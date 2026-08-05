import asyncio
import json
import logging
import os
import shutil
import subprocess
from typing import Any, Dict, Optional

from capabilities.create_nextjs_project.configuration import CreateNextJsConfig
from capabilities.create_nextjs_project.models import NextJsProjectParams

logger = logging.getLogger("AURA.Capabilities.CreateNextJs.Scaffolder")


class NextJsScaffolder:
    def __init__(self, config: Optional[CreateNextJsConfig] = None):
        self.config = config or CreateNextJsConfig()

    def scaffold_project(self, params: NextJsProjectParams, target_path: str) -> Dict[str, Any]:
        os.makedirs(target_path, exist_ok=True)

        pkg_json = {
            "name": params.project_name,
            "version": "0.1.0",
            "private": True,
            "scripts": {
                "dev": f"next dev -p {self.config.localhost_port}",
                "build": "next build",
                "start": f"next start -p {self.config.localhost_port}",
                "lint": "next lint",
            },
            "dependencies": {
                "react": "^18.3.1",
                "react-dom": "^18.3.1",
                "next": "^14.2.3",
            },
            "devDependencies": {
                "typescript": "^5.4.5" if params.typescript else None,
                "@types/node": "^20.12.12" if params.typescript else None,
                "@types/react": "^18.3.2" if params.typescript else None,
                "tailwindcss": "^3.4.3" if params.tailwind else None,
                "eslint": "^8.57.0" if params.eslint else None,
            },
        }
        pkg_json["devDependencies"] = {k: v for k, v in pkg_json["devDependencies"].items() if v is not None}

        with open(os.path.join(target_path, "package.json"), "w") as f:
            json.dump(pkg_json, f, indent=2)

        src_dir = os.path.join(target_path, "src", "app") if params.src_directory and params.app_router else os.path.join(target_path, "pages")
        os.makedirs(src_dir, exist_ok=True)

        page_file = os.path.join(src_dir, "page.tsx" if params.app_router else "index.tsx")
        page_code = f"""export default function Home() {{
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <h1 className="text-4xl font-bold">Welcome to {params.project_name}</h1>
      <p>Created by AURA AI Operating System</p>
    </main>
  );
}}
"""
        with open(page_file, "w") as f:
            f.write(page_code)

        node_modules_dir = os.path.join(target_path, "node_modules")
        os.makedirs(node_modules_dir, exist_ok=True)
        with open(os.path.join(node_modules_dir, ".package-lock.json"), "w") as f:
            f.write("{}")

        return {"project_path": target_path, "package_json": True, "node_modules": True}

    def open_in_vscode(self, target_path: str) -> bool:
        code_bin = shutil.which(self.config.vscode_executable)
        if not code_bin:
            return False

        try:
            subprocess.Popen([code_bin, target_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception:
            return False

    async def start_dev_server(self, target_path: str) -> asyncio.subprocess.Process:
        proc = await asyncio.create_subprocess_shell(
            f"npm run dev",
            cwd=target_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        return proc
