import logging

logger = logging.getLogger("AURA.Speech.TTS.Legacy")


class TTS:
    """
    Legacy Text-to-Speech manager using edge_provider or fallbacks.
    Backward compatibility helper class.
    """

    def __init__(self, provider: str = "edge"):
        self.provider = provider

    def speak(self, text: str, output_file: str = "output.wav") -> str:
        try:
            from speech.providers.edge_provider import speak as speak_edge
            speak_edge(text)
            return output_file
        except Exception as e:
            logger.error(f"Legacy TTS synthesis error: {e}")
            return ""
