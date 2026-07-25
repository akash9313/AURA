import asyncio
import os
import edge_tts

TEXT = "Hello Akash. Welcome to AURA."
VOICE = "en-US-AriaNeural"
OUTPUT = "hello.mp3"


async def main():
    print(f"Generating speech with voice '{VOICE}'...")
    communicate = edge_tts.Communicate(TEXT, VOICE)
    await communicate.save(OUTPUT)
    
    abs_path = os.path.abspath(OUTPUT)
    file_size = os.path.getsize(abs_path)
    print(f"[SUCCESS] Audio saved to: {abs_path} ({file_size} bytes)")
    
    # Optionally open/play the audio file on Windows
    print("Playing generated audio...")
    os.startfile(abs_path)


if __name__ == "__main__":
    asyncio.run(main())