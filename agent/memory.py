"""
TaskMate AI - Conversation Memory System
Manages conversation history and context for personalized AI responses.
"""

from typing import List, Dict, Optional
from datetime import datetime


class ConversationMemory:
    """Manages conversation context and memory for each user."""

    def __init__(self, db, max_messages: int = 10):
        self.db = db
        self.max_messages = max_messages
        self._cache: Dict[str, List[dict]] = {}

    def add_message(self, user_phone: str, role: str, content: str, intent: str = ""):
        """Add a message to memory and persist to database."""
        self.db.save_message(user_phone, role, content, intent)

        # Update cache
        if user_phone not in self._cache:
            self._cache[user_phone] = []

        self._cache[user_phone].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

        # Trim cache to max messages
        if len(self._cache[user_phone]) > self.max_messages:
            self._cache[user_phone] = self._cache[user_phone][-self.max_messages:]

    def get_context(self, user_phone: str) -> List[dict]:
        """Get conversation context for GPT prompt building."""
        if user_phone not in self._cache:
            # Load from database
            history = self.db.get_conversation_history(user_phone, self.max_messages)
            self._cache[user_phone] = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in history
            ]

        return self._cache[user_phone]

    def get_context_summary(self, user_phone: str) -> str:
        """Get a text summary of recent context for enhanced prompts."""
        context = self.get_context(user_phone)
        if not context:
            return "No previous conversation history."

        summary_parts = []
        for msg in context[-5:]:
            role_label = "User" if msg["role"] == "user" else "Assistant"
            summary_parts.append(f"{role_label}: {msg['content'][:100]}")

        return "\n".join(summary_parts)

    def build_gpt_messages(self, user_phone: str, system_prompt: str, current_message: str) -> List[dict]:
        """Build the full message array for GPT API call."""
        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history
        context = self.get_context(user_phone)
        for msg in context:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # Add current message
        messages.append({"role": "user", "content": current_message})

        return messages

    def clear_context(self, user_phone: str):
        """Clear conversation context for a user."""
        if user_phone in self._cache:
            del self._cache[user_phone]

    def get_user_profile_context(self, user_phone: str) -> str:
        """Build a user profile context string from conversation patterns."""
        context = self.get_context(user_phone)
        if not context:
            return ""

        # Analyze user messages for profile building
        user_messages = [msg["content"] for msg in context if msg["role"] == "user"]
        if not user_messages:
            return ""

        return f"User has sent {len(user_messages)} recent messages. Recent topics discussed in context."
