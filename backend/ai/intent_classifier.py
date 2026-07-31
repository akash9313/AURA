import os
import json
from ai.providers.gemini_provider import ask_gemini

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "prompts", "system_prompt.txt")

with open(PROMPT_PATH, encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()


def classify(text):

    response = ask_gemini(
        SYSTEM_PROMPT,
        text
    )

    return json.loads(response)