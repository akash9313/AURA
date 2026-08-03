import logging

logger = logging.getLogger("AURA.Speech.TTS")


class TTS:
    """
    Text-to-Speech manager using edge_provider or fallbacks.
    """

    def __init__(self, provider: str = "edge"):
        self.provider = provider

    def speak(self, text: str, output_file: str = "output.wav") -> str:
        """Synthesize speech using selected provider."""
        try:
            from speech.providers.edge_provider import speak as speak_edge
            speak_edge(text)
            return output_file
        except Exception as e:
            logger.error(f"TTS synthesis error: {e}")
            return ""
