"""
Conversation Manager Unit, Lifecycle, Interruption, Follow-up Timeout, and Cancellation Test Suite.
Tests ConversationSession, ConversationStateMachine, ConversationContext, InterruptionHandler, ConversationManager, and ConversationService.
"""

import asyncio
import sys
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, ".")

from conversation.models import ConversationSession, ConversationState, InterruptionPayload
from conversation.events import ConversationEvent
from conversation.configuration import ConversationConfig
from conversation.context import ConversationContext
from conversation.state_machine import ConversationStateMachine
from conversation.interruption import InterruptionHandler
from conversation.conversation_manager import ConversationManager
from conversation.service import ConversationService


class TestConversationManager(unittest.TestCase):
    """Test suite for Conversation Manager subsystem."""

    def setUp(self):
        self.bus = MagicMock()
        self.config = ConversationConfig(followup_timeout_sec=0.1)
        self.manager = ConversationManager(bus=self.bus, config=self.config)
        self.service = ConversationService(bus=self.bus, config=self.config)

    def test_full_conversation_lifecycle(self):
        """
        IDLE -> LISTENING -> TRANSCRIBING -> THINKING -> RESPONDING -> WAITING_FOR_FOLLOWUP -> IDLE
        """
        session = self.manager.start_conversation(wake_word="hey aura")
        self.assertEqual(session.current_state, ConversationState.LISTENING)

        # STT Completed -> TRANSCRIBING -> THINKING
        self.manager.on_transcription_completed("Open Notepad")
        self.assertEqual(session.current_state, ConversationState.THINKING)
        self.assertEqual(len(self.manager.context.get_history()), 1)

        # LLM Completed -> RESPONDING
        self.manager.on_llm_completed("Opening Notepad app now.")
        self.assertEqual(session.current_state, ConversationState.RESPONDING)
        self.assertEqual(len(self.manager.context.get_history()), 2)

        # TTS Completed -> WAITING_FOR_FOLLOWUP
        self.manager.on_tts_completed()
        self.assertEqual(session.current_state, ConversationState.WAITING_FOR_FOLLOWUP)

        # End Conversation -> IDLE
        self.manager.end_conversation()
        self.assertEqual(session.current_state, ConversationState.IDLE)

        # Verify EventBus events published
        published = [call[0][0] for call in self.bus.publish.call_args_list]
        self.assertIn("conversation_started", published)
        self.assertIn("listening_started", published)
        self.assertIn("transcription_completed", published)
        self.assertIn("llm_started", published)
        self.assertIn("llm_completed", published)
        self.assertIn("tts_started", published)
        self.assertIn("tts_completed", published)
        self.assertIn("conversation_ended", published)

    def test_user_interruption_during_tts(self):
        """User starts speaking while TTS is active -> Stop TTS, return to LISTENING."""
        session = self.manager.start_conversation(wake_word="hey aura")
        self.manager.on_transcription_completed("Search the web")
        self.manager.on_llm_completed("Searching web for you.")
        self.assertEqual(session.current_state, ConversationState.RESPONDING)

        # User interrupts!
        self.manager.handle_user_interruption()
        self.assertEqual(session.current_state, ConversationState.LISTENING)
        self.assertEqual(session.interruption_count, 1)

        # Verify interruption events
        published = [call[0][0] for call in self.bus.publish.call_args_list]
        self.assertIn("user_interrupted", published)
        self.assertIn("tts_cancelled", published)
        self.assertIn("audio_queue_flushed", published)

    def test_followup_mode_timeout(self):
        """Follow-up timeout elapses -> Returns to IDLE."""
        session = self.manager.start_conversation(wake_word="hey aura")
        self.manager.on_transcription_completed("Hello")
        self.manager.on_llm_completed("Hi there!")
        self.manager.on_tts_completed()
        self.assertEqual(session.current_state, ConversationState.WAITING_FOR_FOLLOWUP)

        # Run timeout wait
        asyncio.run(self.manager._wait_for_followup_timeout())
        self.assertEqual(session.current_state, ConversationState.IDLE)


if __name__ == "__main__":
    unittest.main()
