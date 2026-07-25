import os
from dotenv import load_dotenv

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")


def speak_elevenlabs(text, voice_id="21m00Tcm4TlvDq8ikWAM", output_file="output.wav"):
    """
    Synthesize speech using ElevenLabs API.
    """
    if not ELEVENLABS_API_KEY:
        print("[ElevenLabs TTS] Warning: ELEVENLABS_API_KEY not found in .env")
        return None

    print(f"[ElevenLabs TTS] Synthesizing: '{text}'")
    # ElevenLabs API integration logic goes here
    return output_file
