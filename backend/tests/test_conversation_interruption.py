import time
import unittest
from core.events import Event
from core.event_bus import EventBus
from conversation.audio_focus import AudioFocusManager
from conversation.cancellation import CancellationManager
from conversation.conversation_state import ConversationStateMachine
from conversation.coordinator import ConversationCoordinator
from conversation.events import ConversationEvent
from conversation.interruption import InterruptionDetector
from conversation.models import ConversationState, InterruptionPayload
from conversation.service import ConversationService
from speech.vad.events import VADEvent


class TestConversationInterruption(unittest.TestCase):

    def setUp(self):
        self.bus = EventBus()
        self.state_machine = ConversationStateMachine()
        self.audio_focus = AudioFocusManager()
        self.cancellation_mgr = CancellationManager(bus=self.bus)
        self.interruption_detector = InterruptionDetector()
        self.coordinator = ConversationCoordinator(bus=self.bus)
        self.service = ConversationService(bus=self.bus)

    def test_state_machine_transitions(self):
        """Test clean state machine transitions."""
        self.assertEqual(self.state_machine.current_state, ConversationState.IDLE)
        self.assertTrue(self.state_machine.transition_to(ConversationState.LISTENING))
        self.assertTrue(self.state_machine.transition_to(ConversationState.THINKING))
        self.assertTrue(self.state_machine.transition_to(ConversationState.SPEAKING))
        self.assertTrue(self.state_machine.transition_to(ConversationState.INTERRUPTED))
        self.assertTrue(self.state_machine.transition_to(ConversationState.LISTENING))
        self.assertEqual(self.state_machine.current_state, ConversationState.LISTENING)

    def test_audio_focus_management(self):
        """Test AudioFocus focus acquisition and restoration."""
        self.audio_focus.acquire_speaker_focus()
        self.assertTrue(self.audio_focus.is_speaker_active)

        self.audio_focus.restore_mic_focus()
        self.assertFalse(self.audio_focus.is_speaker_active)
        self.assertTrue(self.audio_focus.is_mic_enabled)

    def test_sub_100ms_cancellation_manager(self):
        """Test sub-100ms cancellation manager latency target."""
        res = self.cancellation_mgr.execute_cancellation(reason="test_interruption")
        self.assertLess(res["cancellation_latency_ms"], 100.0)
        self.assertIn("streaming_llm", res["flushed_components"])

    def test_interruption_detector_evaluation(self):
        """Test InterruptionDetector triggers only during THINKING or SPEAKING."""
        payload_idle = self.interruption_detector.evaluate_voice_activity(ConversationState.IDLE, "s1")
        self.assertIsNone(payload_idle)

        payload_speaking = self.interruption_detector.evaluate_voice_activity(ConversationState.SPEAKING, "s1")
        self.assertIsNotNone(payload_speaking)
        self.assertEqual(payload_speaking.interrupted_state, ConversationState.SPEAKING)

    def test_sub_150ms_coordinator_interruption(self):
        """Test ConversationCoordinator handles interruption within <150ms target."""
        self.coordinator.handle_text_ready("Prompt text")
        self.coordinator.handle_llm_token({"token": "Hello"})
        self.assertEqual(self.coordinator.state_machine.current_state, ConversationState.SPEAKING)

        t0 = time.time()
        self.coordinator.handle_voice_started()
        dt_ms = (time.time() - t0) * 1000.0

        self.assertLess(dt_ms, 150.0)
        self.assertEqual(self.coordinator.state_machine.current_state, ConversationState.LISTENING)
        self.assertEqual(self.coordinator.session.interruption_count, 1)

    def test_conversation_service_event_interruption_lifecycle(self):
        """Test ConversationService responds to VAD voice events during SPEAKING and emits USER_INTERRUPTED."""
        self.service.start()
        received_events = []

        def event_listener(evt, payload):
            received_events.append((evt, payload))

        self.bus.subscribe(ConversationEvent.USER_INTERRUPTED.value, lambda p: event_listener(ConversationEvent.USER_INTERRUPTED.value, p))
        self.bus.subscribe(ConversationEvent.CONVERSATION_RESUMED.value, lambda p: event_listener(ConversationEvent.CONVERSATION_RESUMED.value, p))

        # Simulate AURA reasoning & speaking
        self.bus.publish(Event.TEXT_READY, "Tell me about AI")
        self.bus.publish(Event.STREAMING_RESPONSE, {"token": "Artificial"})

        # User interrupts!
        self.bus.publish(VADEvent.VOICE_STARTED.value, {})

        event_names = [evt for evt, _ in received_events]
        self.assertIn(ConversationEvent.USER_INTERRUPTED.value, event_names)
        self.assertIn(ConversationEvent.CONVERSATION_RESUMED.value, event_names)


if __name__ == "__main__":
    unittest.main()
