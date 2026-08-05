"""
Voice Interruption Handler.
Detects user speech interruptions while TTS is active, stops TTS immediately, flushes audio queue, and returns to LISTENING.
"""

import logging
import time
from typing import Any, Dict, Optional

from conversation.events import ConversationEvent
from conversation.models import ConversationSession, ConversationState, InterruptionPayload

logger = logging.getLogger("AURA.Conversation.Interruption")


class InterruptionHandler:
    """
    Handles user speech interruptions during TTS voice responses.
    """

    def __init__(self, bus: Any = None):
        self.bus = bus

    def handle_interruption(
        self,
        session: ConversationSession,
        current_state: ConversationState,
    ) -> InterruptionPayload:
        """
        Stop active TTS output, flush audio queue, and record interruption telemetry.

        Returns:
            InterruptionPayload object.
        """
        start = time.time()
        logger.info(f"User interrupted active voice response in state '{current_state.value}'!")
        session.interruption_count += 1

        payload = InterruptionPayload(
            session_id=session.session_id,
            interrupted_state=current_state,
            interruption_latency_ms=(time.time() - start) * 1000.0,
        )

        self._publish_event(ConversationEvent.USER_INTERRUPTED, payload.to_dict())
        self._publish_event(ConversationEvent.TTS_CANCELLED, {"session_id": session.session_id})
        self._publish_event(ConversationEvent.AUDIO_QUEUE_FLUSHED, {"session_id": session.session_id})
        self._publish_event(ConversationEvent.CONVERSATION_INTERRUPTED, payload.to_dict())

        return payload

    def _publish_event(self, event: ConversationEvent, data: Dict[str, Any]) -> None:
        if self.bus:
            try:
                self.bus.publish(event.value, data)
            except Exception as e:
                logger.error(f"Failed to publish interruption event '{event.value}': {e}")
