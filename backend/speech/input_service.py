from core.service import Service
from core.events import Event

from speech.recorder import record_audio
from speech.stt import speech_to_text


class InputService(Service):

    def start(self):

        print("Input Service Started")

        while True:

            user_choice = input("\nPress ENTER to speak (or type 't' to type input): ")

            if user_choice.strip().lower() == 't':
                text = input("\n👤 Enter text: ").strip()
            else:
                audio = record_audio()
                text = speech_to_text(audio)
                if not text:
                    text = input("⚠️ Speech recognition was empty or unavailable. Type your prompt: ").strip()

            if text:

                print(f"\n👤 {text}")

                self.bus.publish(
                    Event.TEXT_READY,
                    text
                )

    def stop(self):

        print("Input Service Stopped")