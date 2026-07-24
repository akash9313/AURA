from ai.providers.gemini_provider import ask_gemini


class LLM:

    def chat(self, message):

        return ask_gemini(message)