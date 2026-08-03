import logging
import time
from typing import Dict, Any
from speech.streaming.models import LatencyMetrics

logger = logging.getLogger("AURA.Speech.Latency")


class LatencyMonitor:
    """
    Monitors latency telemetry across all voice pipeline stages.
    """

    def __init__(self):
        self.metrics = LatencyMetrics()
        self._start_time: float = 0.0

    def start_turn(self) -> None:
        self._start_time = time.time()

    def record_stt(self, duration_ms: float) -> None:
        self.metrics.stt_latency_ms = duration_ms

    def record_llm_first_token(self, duration_ms: float) -> None:
        self.metrics.llm_latency_ms = duration_ms

    def record_tts(self, duration_ms: float) -> None:
        self.metrics.tts_latency_ms = duration_ms

    def finalize_turn(self) -> LatencyMetrics:
        if self._start_time > 0:
            self.metrics.total_roundtrip_ms = (time.time() - self._start_time) * 1000.0
        logger.info(
            f"⏱️ Voice Turn Latency Breakdown: Total={self.metrics.total_roundtrip_ms:.1f}ms | "
            f"STT={self.metrics.stt_latency_ms:.1f}ms | LLM={self.metrics.llm_latency_ms:.1f}ms | "
            f"TTS={self.metrics.tts_latency_ms:.1f}ms"
        )
        return self.metrics
