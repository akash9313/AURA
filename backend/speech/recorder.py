import sounddevice as sd
import soundfile as sf

SAMPLE_RATE = 16000
CHANNELS = 1


def record_audio(filename="audio.wav", duration=5):
    """
    Record audio from default microphone for specified duration and save as 16-bit WAV file.
    """
    print(f"\n🎤 Recording... Speak now ({duration} seconds)...")

    recording = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="int16"
    )

    sd.wait()

    sf.write(filename, recording, SAMPLE_RATE, subtype='PCM_16')

    print(f"✅ Recording saved as '{filename}'")

    return filename