from speech.recorder import record_audio
from speech.stt import speech_to_text

from ai.llm import LLM

assistant = LLM()


def main():

    print("=" * 50)
    print("AURA Voice Assistant")
    print("=" * 50)

    input("Press ENTER to speak...")

    audio = record_audio()

    print("\nTranscribing...\n")

    user_text = speech_to_text(audio)

    print("You:", user_text)

    print("\nThinking...\n")

    reply = assistant.chat(user_text)

    print("AURA:", reply)


if __name__ == "__main__":
    main()