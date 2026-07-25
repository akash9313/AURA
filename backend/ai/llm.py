from ai.providers.gemini_provider import ask_gemini


def ask_ai(prompt):
    return ask_gemini(prompt)


class LLM:

    def chat(self, message):
        return ask_ai(message)