import logging
from typing import List, Tuple
from config.models import AppConfig

logger = logging.getLogger("AURA.Config.Validator")


class ConfigValidator:
    """Configuration Schema & Value Validator."""

    def validate(self, config: AppConfig) -> Tuple[bool, List[str]]:
        errors: List[str] = []

        # 1. Validate STT latency settings
        stt_cat = config.categories.get("stt")
        if stt_cat:
            partial_target = stt_cat.get("partial_latency_target_ms", 300.0)
            if not isinstance(partial_target, (int, float)) or partial_target <= 0:
                errors.append(f"STT partial_latency_target_ms must be a positive number, got: {partial_target}")

        # 2. Validate LLM settings
        llm_cat = config.categories.get("llm")
        if llm_cat:
            temp = llm_cat.get("temperature", 0.7)
            if not (0.0 <= temp <= 2.0):
                errors.append(f"LLM temperature must be between 0.0 and 2.0, got: {temp}")

        # 3. Validate TTS settings
        tts_cat = config.categories.get("tts")
        if tts_cat:
            vol = tts_cat.get("volume", 1.0)
            if not (0.0 <= vol <= 2.0):
                errors.append(f"TTS volume must be between 0.0 and 2.0, got: {vol}")

        is_valid = len(errors) == 0
        if not is_valid:
            logger.warning(f"Configuration Validation Failed: {len(errors)} errors found.")
            for err in errors:
                logger.warning(f" Validation Error: {err}")
        else:
            logger.info("Configuration Validation Passed Cleanly.")

        return is_valid, errors
