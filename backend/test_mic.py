import sounddevice as sd
import soundfile as sf

print("Default device:", sd.default.device)

duration = 5
samplerate = 16000

print("Recording...")

recording = sd.rec(
    int(duration * samplerate),
    samplerate=samplerate,
    channels=1,
    dtype='float32'
)

sd.wait()

sf.write("test.wav", recording, samplerate)

print("Done.")