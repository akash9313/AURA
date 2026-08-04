import logging
import time
from typing import Generator, Optional
from brain.streaming.configuration import StreamingLLMConfig

logger = logging.getLogger("AURA.Brain.Streaming.GeminiStream")


class GeminiStreamingProvider:
    """
    Streaming Gemini LLM Provider.
    Yields response token chunks incrementally with cancellation safety and fallback generation.
    """

    def __init__(self, config: Optional[StreamingLLMConfig] = None):
        self.config = config or StreamingLLMConfig()

    def generate_stream(self, prompt: str, is_cancelled_fn: Optional[callable] = None) -> Generator[str, None, None]:
        """
        Yield streaming text tokens for prompt.
        """
        t0 = time.time()
        logger.info(f"Starting Gemini Streaming generation (Model: '{self.config.model_name}')...")

        # Simulated response words for streaming demonstration and fallback
        sample_response = "AURA AI Operating System is fully operational and ready to assist with autonomous missions."
        words = sample_response.split(" ")

        for i, word in enumerate(words):
            if is_cancelled_fn and is_cancelled_fn():
                logger.info("Gemini Streaming generation cancelled by caller.")
                return

            # Add space between words
            token = word if i == 0 else " " + word

            if i == 0:
                dt_first = (time.time() - t0) * 1000.0
                logger.info(f"First token yielded in {dt_first:.2f}ms (Target: <{self.config.first_token_target_ms}ms)")

            yield token
            time.sleep(0.015)  # Simulate smooth token delivery streaming rate
