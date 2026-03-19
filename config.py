"""
TaskMate AI - Configuration Module
Loads environment variables and provides default configuration values.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Central configuration for TaskMate AI."""

    # Hugging Face
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
    HUGGINGFACE_MODEL = os.getenv("HUGGINGFACE_MODEL", "Qwen/Qwen2.5-72B-Instruct")

    # Twilio
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

    # Weather API
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

    # Database
    DATABASE_PATH = os.getenv("DATABASE_PATH", "taskmate.db")

    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"

    # Agent
    MAX_MEMORY_MESSAGES = int(os.getenv("MAX_MEMORY_MESSAGES", "10"))
    SYSTEM_PROMPT = """You are TaskMate AI, a highly intelligent and friendly WhatsApp productivity assistant.
Your personality: Professional yet warm, proactive, concise, and action-oriented.

Your capabilities:
- Set reminders and manage tasks
- Summarize long text or notes
- Fetch real-time weather information
- Have smart, context-aware conversations
- Make proactive suggestions to boost productivity

Rules:
- Keep responses concise (WhatsApp-friendly, under 500 chars when possible)
- Use emojis naturally but not excessively
- Always confirm actions taken
- Suggest follow-up actions when appropriate
- Be proactive: if a user mentions a meeting, suggest setting a reminder
- Format responses cleanly with line breaks for readability
"""

    @classmethod
    def validate(cls):
        """Validate that critical configuration is set."""
        warnings = []
        if not cls.HUGGINGFACE_API_KEY:
            warnings.append("⚠️  HUGGINGFACE_API_KEY is not set")
        if not cls.TWILIO_ACCOUNT_SID:
            warnings.append("⚠️  TWILIO_ACCOUNT_SID is not set")
        if not cls.TWILIO_AUTH_TOKEN:
            warnings.append("⚠️  TWILIO_AUTH_TOKEN is not set")
        if not cls.OPENWEATHER_API_KEY:
            warnings.append("⚠️  OPENWEATHER_API_KEY is not set (weather feature disabled)")
        return warnings
