from google import genai

from core.config import GEMINI_API_KEY
from ai.prompts import SYSTEM_PROMPT

client = genai.Client(api_key=GEMINI_API_KEY)


def ask_gemini(arg1, arg2=None):

    if arg2 is not None:
        sys_prompt = arg1
        user_message = arg2
    else:
        sys_prompt = SYSTEM_PROMPT
        user_message = arg1

    prompt = f"""
{sys_prompt}

User:
{user_message}

Assistant:
"""

    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt
    )

    return response.text