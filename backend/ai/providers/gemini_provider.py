import logging
from google import genai
from google.genai import errors

from core.config import GEMINI_API_KEY
from ai.prompts import SYSTEM_PROMPT

logger = logging.getLogger("AURA.AI.GeminiProvider")

client = genai.Client(api_key=GEMINI_API_KEY)


def ask_gemini(arg1: str, arg2: str = None) -> str:
    """
    Query Gemini LLM with system prompt and user message.
    Handles rate-limiting (429) gracefully without blocking threads.
    """
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

    try:
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=prompt
        )
        return response.text
    except errors.ClientError as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            logger.warning("Gemini API 429 Quota Exhausted. Using fallback response.")
            raise RuntimeError("Gemini API quota exhausted (429)") from e
        logger.error(f"Gemini ClientError: {e}")
        raise e
    except Exception as e:
        logger.error(f"Gemini API Request failed: {e}")
        raise e