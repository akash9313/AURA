import asyncio
import edge_tts
import pygame
import os

VOICE = "en-US-AriaNeural"


async def _generate(text):

    await edge_tts.Communicate(
        text,
        VOICE
    ).save("response.mp3")


def speak(text):

    asyncio.run(_generate(text))

    pygame.mixer.init()

    pygame.mixer.music.load("response.mp3")

    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        continue

    pygame.mixer.quit()

    os.remove("response.mp3")