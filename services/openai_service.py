"""
TaskMate AI - AI Service (Hugging Face)
Handles all interactions with the Hugging Face Inference API via their OpenAI-compatible endpoint.
"""

import httpx
from typing import Optional
from config import Config


class AIService:
    """Wrapper for Hugging Face Inference API interactions."""

    INFERENCE_URL = "https://router.huggingface.co/v1/chat/completions"

    def __init__(self):
        self.api_key = Config.HUGGINGFACE_API_KEY
        self.model = Config.HUGGINGFACE_MODEL
        self.system_prompt = Config.SYSTEM_PROMPT
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def _query_model(self, messages: list, max_tokens: int = 500, temperature: float = 0.7) -> str:
        """Send a query to the Hugging Face v1 Inference API."""
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": 0.9,
                "stream": False
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.INFERENCE_URL,
                    headers=self.headers,
                    json=payload
                )

                if response.status_code == 200:
                    result = response.json()
                    choices = result.get("choices", [])
                    if choices and len(choices) > 0:
                        msg = choices[0].get("message", {}).get("content", "").strip()
                        return msg if msg else "I'm here to help! Try asking me something."
                    return "I'm here to help! Try asking me something."

                elif response.status_code == 503:
                    # Model is loading
                    return "🔄 The AI model is warming up. Please try again in a few seconds!"

                elif response.status_code == 401:
                    return "⚠️ AI authentication error. Please check your Hugging Face API key."

                else:
                    error_detail = response.text[:200]
                    print(f"[HF API Error] Status {response.status_code}: {error_detail}")
                    return "⚠️ Sorry, I encountered an AI error. Please try again."

        except httpx.TimeoutException:
            return "⚠️ The AI took too long to respond. Please try again."
        except Exception as e:
            print(f"[HF Error] {type(e).__name__}: {e}")
            return f"⚠️ Sorry, I encountered an error. Please try again. ({type(e).__name__})"

    async def chat(self, user_phone: str, message: str, memory=None) -> str:
        """Generate a conversational response."""
        if memory:
            messages = memory.build_gpt_messages(
                user_phone=user_phone,
                system_prompt=self.system_prompt,
                current_message=message
            )
        else:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": message}
            ]

        return await self._query_model(messages, max_tokens=500, temperature=0.7)

    async def summarize(self, text: str) -> str:
        """Summarize a given text."""
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a precise text summarizer. Provide a clear, concise summary "
                    "of the given text. Keep it under 150 words. Use bullet points for "
                    "key points if the text is complex. Maintain the core meaning."
                )
            },
            {
                "role": "user",
                "content": f"Please summarize the following text:\n\n{text}"
            }
        ]

        return await self._query_model(messages, max_tokens=300, temperature=0.3)

    async def classify_intent(self, message: str) -> str:
        """Use AI to classify intent when keyword matching is uncertain."""
        messages = [
            {
                "role": "system",
                "content": (
                    "Classify the user message into exactly one category. "
                    "Reply with ONLY the category name, nothing else. "
                    "Categories: reminder, task_create, task_complete, task_list, "
                    "summarize, weather, help, greeting, general."
                )
            },
            {"role": "user", "content": message}
        ]

        try:
            result = await self._query_model(messages, max_tokens=20, temperature=0.1)
            result = result.strip().lower().rstrip(".")

            valid_intents = ["reminder", "task_create", "task_complete", "task_list",
                             "summarize", "weather", "help", "greeting", "general"]

            for intent in valid_intents:
                if intent in result:
                    return intent

            return "general"
        except Exception:
            return "general"
