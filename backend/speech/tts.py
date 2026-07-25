from speech.providers.piper_provider import speak_piper
from speech.providers.elevenlabs_provider import speak_elevenlabs
from speech.providers.azure_provider import speak_azure


class TTS:
    def __init__(self, provider="piper"):
        self.provider = provider

    def speak(self, text, output_file="output.wav"):
        """
        Synthesize text into speech using the configured provider.
        """
        if self.provider == "elevenlabs":
            return speak_elevenlabs(text, output_file=output_file)
        elif self.provider == "azure":
            return speak_azure(text, output_file=output_file)
        else:
            return speak_piper(text, output_file=output_file)
