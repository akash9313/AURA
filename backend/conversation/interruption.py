import logging
import time
from typing import Callable, Optional
from conversation.models import ConversationState, InterruptionPayload

logger = logging.getLogger("AURA.Conversation.InterruptionDetector")


class InterruptionDetector:
    """
    Real-Time Speech Interruption Detector.
    Monitors VAD voice activity and triggers interruption when user speaks during THINKING or SPEAKING states.
    """

    def __init__(self, on_interruption_fn: Optional[Callable[[InterruptionPayload], None]] = None):
        self.on_interruption_fn = on_interruption_fn

    def evaluate_voice_activity(self, current_state: ConversationState, session_id: str) -> Optional[InterruptionPayload]:
        t0 = time.time()

        if current_state in (ConversationState.THINKING, ConversationState.SPEAKING):
            dt_ms = (time.time() - t0) * 1000.0
            logger.info(f"Interruption detected during state '{current_state.value.upper()}' (Latency: {dt_ms:.2f}ms)")

            payload = InterruptionPayload(
                session_id=session_id,
                interrupted_state=current_state,
                interruption_latency_ms=dt_ms
            )

            if self.on_interruption_fn:
                try:
                    self.on_interruption_fn(payload)
                except Exception as e:
                    logger.error(f"Error executing interruption callback: {e}")

            return payload

        return None
