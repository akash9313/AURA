import logging
import os
from typing import Dict, List
from developer.models import CodeAnalysisResult, TechStack

logger = logging.getLogger("AURA.Developer.CodeAnalyzer")


class CodeAnalyzer:
    """
    Multi-language static code analyzer for Python, JS, TS, Rust, Go, Java, C++, Dart.
    """

    EXT_MAP = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".jsx": "javascript",
        ".tsx": "typescript",
        ".rs": "rust",
        ".go": "go",
        ".java": "java",
        ".cpp": "cpp",
        ".c": "c",
        ".dart": "dart",
    }

    def analyze_project(self, project_path: str) -> CodeAnalysisResult:
        total_lines = 0
        langs = set()

        for root, _, files in os.walk(project_path):
            if ".git" in root or "node_modules" in root or "venv" in root:
                continue
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in self.EXT_MAP:
                    langs.add(self.EXT_MAP[ext])
                    try:
                        with open(os.path.join(root, f), "r", encoding="utf-8", errors="ignore") as fh:
                            total_lines += len(fh.readlines())
                    except Exception:
                        pass

        tech = TechStack.PYTHON
        if "typescript" in langs:
            tech = TechStack.TYPESCRIPT
        elif "javascript" in langs:
            tech = TechStack.JAVASCRIPT
        elif "rust" in langs:
            tech = TechStack.RUST
        elif "go" in langs:
            tech = TechStack.GO

        summary = f"Detected project containing {len(langs)} languages with approximately {total_lines} total lines of code."
        arch = f"Modular project structure utilizing {', '.join(sorted(langs))} codebase organization."

        return CodeAnalysisResult(
            tech_stack=tech,
            languages_detected=list(langs),
            total_lines_of_code=total_lines,
            summary=summary,
            architecture_overview=arch
        )
