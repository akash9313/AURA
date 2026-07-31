import unittest
from unittest.mock import MagicMock, patch
from core.events import Event
from brain.brain_service import BrainService


class TestBrainService(unittest.TestCase):

    def setUp(self):
        self.bus = MagicMock()
        self.service = BrainService(self.bus)

    @patch("brain.brain_service.classify")
    def test_on_text_ready(self, mock_classify):
        mock_classify.return_value = {
            "intent": "open_application",
            "parameters": {"application": "chrome"}
        }

        self.service.on_text_ready("open chrome")

        mock_classify.assert_called_once_with("open chrome")
        self.bus.publish.assert_called_once()
        event, intent = self.bus.publish.call_args[0]
        self.assertEqual(event, Event.INTENT_READY)
        self.assertEqual(intent.name, "open_application")
        self.assertEqual(intent.parameters, {"application": "chrome"})


if __name__ == "__main__":
    unittest.main()
