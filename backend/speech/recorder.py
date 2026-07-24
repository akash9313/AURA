import sounddevice as sd
import soundfile as sf

SAMPLE_RATE = 16000
CHANNELS = 1

def record_audio(filename="audio.wav", duration=5):
    print("\n🎤 Recording... Speak now.")

    recording = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="float32"
    )

    sd.wait()

    sf.write(filename, recording, SAMPLE_RATE)

    print("✅ Recording saved as", filename)

    return filename