import sys
import threading
from core.events import Event
from core.service import Service

from speech.recorder import record_audio
from speech.stt import speech_to_text


class InputService(Service):

    def __init__(self, bus=None):
        super().__init__(bus)
        self._running = False
        self._thread = None

    def start(self):
        print("Input Service Started")
        self._running = True
        self._thread = threading.Thread(target=self._input_loop, daemon=True)
        self._thread.start()

    def _input_loop(self):
        while self._running:
            try:
                if not sys.stdin.isatty():
                    break

                user_choice = input("\nPress ENTER to speak (or type 't' to type input): ")

                if user_choice.strip().lower() == 't':
                    text = input("\n👤 Enter text: ").strip()
                else:
                    audio = record_audio()
                    text = speech_to_text(audio)
                    if not text:
                        text = input("⚠️ Speech recognition was empty or unavailable. Type your prompt: ").strip()

                if text and self.bus:
                    print(f"\n👤 {text}")
                    self.bus.publish(
                        Event.TEXT_READY,
                        text
                    )

            except (EOFError, KeyboardInterrupt):
                break
            except Exception:
                if not self._running:
                    break

    def stop(self):
        self._running = False
        print("Input Service Stopped")
