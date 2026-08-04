import logging
from typing import Any, Dict, List, Optional
from brain.streaming.configuration import StreamingLLMConfig

logger = logging.getLogger("AURA.Brain.Streaming.ContextBuilder")


class ContextBuilder:
    """
    Assembles prompt context for Streaming Gemini using System Prompt, Conversation History, Memory, and Query.
    """

    def __init__(self, config: Optional[StreamingLLMConfig] = None):
        self.config = config or StreamingLLMConfig()
        self.history: List[Dict[str, str]] = []

    def add_history(self, role: str, text: str) -> None:
        self.history.append({"role": role, "text": text})
        if len(self.history) > 20:
            self.history = self.history[-20:]

    def build_prompt_context(self, user_query: str, memory_context: Optional[str] = None) -> str:
        prompt_parts = [f"System: {self.config.system_prompt}"]

        if memory_context:
            prompt_parts.append(f"Memory Context: {memory_context}")

        if self.history:
            prompt_parts.append("Recent Conversation History:")
            for turn in self.history[-6:]:
                prompt_parts.append(f"{turn['role'].capitalize()}: {turn['text']}")

        prompt_parts.append(f"User: {user_query}")
        prompt_parts.append("AURA:")

        full_prompt = "\n\n".join(prompt_parts)
        logger.info(f"Built prompt context ({len(full_prompt)} chars) for query: '{user_query[:40]}...'")
        return full_prompt
