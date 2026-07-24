from google import genai

from core.config import GEMINI_API_KEY
from ai.prompts import SYSTEM_PROMPT

client = genai.Client(api_key=GEMINI_API_KEY)


def ask_gemini(user_message):

    prompt = f"""
{SYSTEM_PROMPT}

User:
{user_message}

Assistant:
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text