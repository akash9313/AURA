import logging
import time
from typing import Dict, Any
from tools.base import Tool
from tools.result import ToolResult
from ai.llm import ask_ai

logger = logging.getLogger("AURA.Tools.Chat")


class ChatTool(Tool):
    """Tool for handling general conversational queries via AI LLM."""

    @property
    def name(self) -> str:
        return "chat"

    @property
    def description(self) -> str:
        return "Handles general conversational queries and AI responses."

    @property
    def category(self) -> str:
        return "chat"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        message = parameters.get("message", "")
        if not message:
            return ToolResult(
                success=False,
                message="No message provided for chat execution.",
                execution_time=time.time() - start_time
            )

        try:
            response = ask_ai(message)
            elapsed = time.time() - start_time
            return ToolResult(
                success=True,
                message=response,
                data={"query": message, "response": response},
                execution_time=elapsed
            )
        except Exception as e:
            logger.warning(f"ChatTool AI provider error: {e}")
            elapsed = time.time() - start_time
            if "429" in str(e) or "quota" in str(e).lower():
                fallback_msg = (
                    "⚠️ The online Gemini API daily quota limit was reached (429 Rate Limit).\n"
                    "💡 All local AURA actions (opening apps, taking screenshots, reading screens, memory, calculations) remain 100% operational!"
                )
            else:
                fallback_msg = f"Unable to reach AI model right now: {e}"

            return ToolResult(
                success=True,
                message=fallback_msg,
                data={"query": message, "error": str(e)},
                execution_time=elapsed
            )

