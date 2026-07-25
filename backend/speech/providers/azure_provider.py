import os
from dotenv import load_dotenv

load_dotenv()

AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION", "eastus")


def speak_azure(text, output_file="output.wav"):
    """
    Synthesize speech using Azure Speech Service.
    """
    if not AZURE_SPEECH_KEY:
        print("[Azure TTS] Warning: AZURE_SPEECH_KEY not found in .env")
        return None

    print(f"[Azure TTS] Synthesizing: '{text}'")
    # Azure Speech SDK logic goes here
    return output_file
