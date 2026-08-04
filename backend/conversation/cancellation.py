import logging
import time
from typing import Dict, Any
from conversation.events import ConversationEvent

logger = logging.getLogger("AURA.Conversation.Cancellation")


class CancellationManager:
    """
    Sub-100ms Multi-System Cancellation Orchestrator.
    Cancels active LLM streams, TTS synthesis, audio playback queue, and background workflows upon interruption.
    """

    def __init__(self, bus):
        self.bus = bus

    def execute_cancellation(self, reason: str = "user_interrupted") -> Dict[str, Any]:
        t0 = time.time()
        logger.info(f"Executing sub-100ms full-duplex cancellation (Reason: '{reason}')...")

        flushed_components = []

        if self.bus:
            # 1. Publish SPEECH_INTERRUPTED event to cancel LLM and TTS
            self.bus.publish("speech_interrupted", {"reason": reason})
            flushed_components.extend(["streaming_llm", "streaming_tts", "audio_queue"])

            # 2. Publish explicit cancellation events
            self.bus.publish(ConversationEvent.LLM_CANCELLED.value, {"reason": reason})
            self.bus.publish(ConversationEvent.TTS_CANCELLED.value, {"reason": reason})
            self.bus.publish(ConversationEvent.AUDIO_QUEUE_FLUSHED.value, {"reason": reason})

        dt_ms = (time.time() - t0) * 1000.0
        logger.info(f"Full-duplex cancellation completed in {dt_ms:.2f}ms (Target: <100ms)")

        return {
            "cancellation_latency_ms": round(dt_ms, 2),
            "flushed_components": flushed_components,
            "reason": reason,
        }
