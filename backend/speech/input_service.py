from core.service import Service
from core.events import Event

from speech.recorder import record_audio
from speech.stt import speech_to_text


class InputService(Service):

    def start(self):

        print("Input Service Started")

        while True:

            input("\nPress ENTER to speak...")

            audio = record_audio()

            text = speech_to_text(audio)

            if text:

                print(f"\n👤 {text}")

                self.bus.publish(
                    Event.TEXT_READY,
                    text
                )

    def stop(self):

        print("Input Service Stopped")