"""
TaskMate AI - Agent Actions
Routes detected intents to appropriate handler functions and generates responses.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional


class ActionRouter:
    """Routes intents to action handlers and generates responses."""

    def __init__(self, db, memory, openai_service, weather_service=None):
        self.db = db
        self.memory = memory
        self.openai_service = openai_service
        self.weather_service = weather_service

        # Map intents to handlers
        self.handlers = {
            "reminder": self.handle_reminder,
            "task_create": self.handle_task_create,
            "task_complete": self.handle_task_complete,
            "task_list": self.handle_task_list,
            "summarize": self.handle_summarize,
            "weather": self.handle_weather,
            "help": self.handle_help,
            "greeting": self.handle_greeting,
            "general": self.handle_general,
        }

    async def route(self, user_phone: str, message: str, intent_data: Dict) -> str:
        """Route the message to the appropriate handler based on intent."""
        intent = intent_data["intent"]
        handler = self.handlers.get(intent, self.handle_general)

        try:
            response = await handler(user_phone, message, intent_data)

            # Add smart suggestions
            suggestion = self.get_smart_suggestion(intent, intent_data)
            if suggestion:
                response += f"\n\n💡 {suggestion}"

            return response
        except Exception as e:
            self.db.log_action(user_phone, "error", str(e))
            return "⚠️ Oops! Something went wrong. Please try again or type *help* to see what I can do."

    # ─── Intent Handlers ─────────────────────────────────────────

    async def handle_reminder(self, user_phone: str, message: str, intent_data: Dict) -> str:
        """Handle reminder creation."""
        entities = intent_data.get("entities", {})
        content = entities.get("content", "")
        time_str = entities.get("time")

        if not content:
            return "📝 What would you like me to remind you about? For example:\n*Remind me to call mom at 5pm*"

        if not time_str:
            # Default to 1 hour from now
            time_str = (datetime.now() + timedelta(hours=1)).isoformat()
            time_display = "1 hour from now"
        else:
            try:
                remind_time = datetime.fromisoformat(time_str)
                time_display = remind_time.strftime("%I:%M %p, %b %d")
            except (ValueError, TypeError):
                time_display = time_str

        reminder = self.db.create_reminder(
            user_phone=user_phone,
            title=content,
            remind_at=time_str,
            description=message
        )

        return (
            f"⏰ *Reminder Set!*\n\n"
            f"📌 {content}\n"
            f"🕐 {time_display}\n"
            f"🆔 #{reminder['id']}\n\n"
            f"I'll remind you when it's time! ✅"
        )

    async def handle_task_create(self, user_phone: str, message: str, intent_data: Dict) -> str:
        """Handle task creation."""
        entities = intent_data.get("entities", {})
        content = entities.get("content", "")
        priority = entities.get("priority", "medium")

        if not content:
            return "📋 What task would you like to add? For example:\n*Add task: Finish project report*"

        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(priority, "🟡")

        task = self.db.create_task(
            user_phone=user_phone,
            title=content,
            priority=priority,
            description=message
        )

        return (
            f"✅ *Task Created!*\n\n"
            f"📌 {content}\n"
            f"{priority_emoji} Priority: {priority.capitalize()}\n"
            f"🆔 #{task['id']}\n\n"
            f"Stay productive! 💪"
        )

    async def handle_task_complete(self, user_phone: str, message: str, intent_data: Dict) -> str:
        """Handle task completion."""
        entities = intent_data.get("entities", {})
        task_identifier = entities.get("task_identifier", "")

        if not task_identifier:
            # Show pending tasks for user to pick from
            tasks = self.db.get_tasks(user_phone=user_phone, status="pending")
            if not tasks:
                return "🎉 You have no pending tasks! You're all caught up!"

            task_list = "\n".join([f"  {i+1}. {t['title']}" for i, t in enumerate(tasks[:5])])
            return f"Which task did you complete?\n\n{task_list}\n\nJust tell me the task name!"

        completed = self.db.complete_task(user_phone, task_identifier)
        if completed:
            return (
                f"🎉 *Task Completed!*\n\n"
                f"✅ ~~{completed['title']}~~\n\n"
                f"Great job! Keep it up! 🚀"
            )
        else:
            return f"🤔 I couldn't find a pending task matching *\"{task_identifier}\"*. Try typing *my tasks* to see your task list."

    async def handle_task_list(self, user_phone: str, message: str, intent_data: Dict) -> str:
        """Handle listing tasks."""
        tasks = self.db.get_tasks(user_phone=user_phone, status="pending")

        if not tasks:
            return "🎉 *No pending tasks!*\nYou're all caught up! Need to add a new task?"

        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        task_lines = []
        for i, task in enumerate(tasks[:10], 1):
            emoji = priority_emoji.get(task["priority"], "🟡")
            task_lines.append(f"{i}. {emoji} {task['title']}")

        task_list = "\n".join(task_lines)

        return (
            f"📋 *Your Tasks* ({len(tasks)} pending)\n\n"
            f"{task_list}\n\n"
            f"Say *done with [task name]* to complete a task!"
        )

    async def handle_summarize(self, user_phone: str, message: str, intent_data: Dict) -> str:
        """Handle text summarization."""
        entities = intent_data.get("entities", {})
        content = entities.get("content", "")

        if not content or len(content) < 20:
            return "📝 Please provide the text you'd like me to summarize. Send a longer message or paste your notes!"

        summary = await self.openai_service.summarize(content)

        return (
            f"📋 *Summary*\n\n"
            f"{summary}\n\n"
            f"_Original: {len(content)} chars → Summary: {len(summary)} chars_"
        )

    async def handle_weather(self, user_phone: str, message: str, intent_data: Dict) -> str:
        """Handle weather queries."""
        if not self.weather_service:
            return "🌤️ Weather feature is currently unavailable. Please set up your OpenWeatherMap API key."

        entities = intent_data.get("entities", {})
        location = entities.get("location", "London")

        weather_data = await self.weather_service.get_weather(location)
        if not weather_data:
            return f"🤔 Sorry, I couldn't find weather data for *{location}*. Try another city name!"

        return self.format_weather_response(weather_data)

    async def handle_help(self, user_phone: str, message: str, intent_data: Dict) -> str:
        """Handle help requests."""
        return (
            "🤖 *TaskMate AI - Your Productivity Assistant*\n\n"
            "Here's what I can do:\n\n"
            "⏰ *Reminders*\n"
            "  _\"Remind me to call mom at 5pm\"_\n"
            "  _\"Set reminder for meeting in 30 minutes\"_\n\n"
            "📋 *Tasks*\n"
            "  _\"Add task: Buy groceries\"_\n"
            "  _\"Show my tasks\"_\n"
            "  _\"Done with groceries\"_\n\n"
            "📝 *Summarize*\n"
            "  _\"Summarize: [paste your long text]\"_\n\n"
            "🌤️ *Weather*\n"
            "  _\"Weather in New York\"_\n"
            "  _\"What's the temperature in London?\"_\n\n"
            "💬 *Chat*\n"
            "  _Ask me anything! I'm here to help._\n\n"
            "Just type naturally — I understand you! 🚀"
        )

    async def handle_greeting(self, user_phone: str, message: str, intent_data: Dict) -> str:
        """Handle greetings."""
        hour = datetime.now().hour
        if hour < 12:
            greeting = "Good morning"
        elif hour < 17:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"

        # Check if user has pending tasks
        tasks = self.db.get_tasks(user_phone=user_phone, status="pending")
        task_note = ""
        if tasks:
            task_note = f"\n\n📋 You have *{len(tasks)}* pending task(s). Say *my tasks* to view them!"

        return (
            f"👋 {greeting}! I'm *TaskMate AI*, your productivity assistant.\n\n"
            f"How can I help you today? Type *help* to see what I can do! 🚀"
            f"{task_note}"
        )

    async def handle_general(self, user_phone: str, message: str, intent_data: Dict) -> str:
        """Handle general conversation using GPT."""
        response = await self.openai_service.chat(
            user_phone=user_phone,
            message=message,
            memory=self.memory
        )
        return response

    # ─── Helper Methods ──────────────────────────────────────────

    def format_weather_response(self, data: dict) -> str:
        """Format weather data into a nice WhatsApp message."""
        weather_emojis = {
            "clear": "☀️", "clouds": "☁️", "rain": "🌧️",
            "drizzle": "🌦️", "thunderstorm": "⛈️", "snow": "❄️",
            "mist": "🌫️", "fog": "🌫️", "haze": "🌫️"
        }

        condition = data.get("condition", "clear").lower()
        emoji = weather_emojis.get(condition, "🌤️")

        return (
            f"{emoji} *Weather in {data['city']}*\n\n"
            f"🌡️ Temperature: *{data['temp']}°C*\n"
            f"🤔 Feels like: {data['feels_like']}°C\n"
            f"💧 Humidity: {data['humidity']}%\n"
            f"💨 Wind: {data['wind_speed']} m/s\n"
            f"📝 {data['description'].capitalize()}\n\n"
            f"_Updated just now_"
        )

    def get_smart_suggestion(self, intent: str, intent_data: Dict) -> Optional[str]:
        """Generate smart follow-up suggestions."""
        suggestions = {
            "reminder": "Tip: You can also add tasks with *\"add task: [your task]\"*",
            "task_create": "Tip: Say *\"my tasks\"* anytime to see your full task list",
            "task_complete": "Tip: Keep the momentum! What's your next task?",
            "weather": "Tip: I can also set reminders if you need to go somewhere!",
            "greeting": None,
            "help": None,
            "general": None,
            "summarize": None,
            "task_list": None,
        }
        return suggestions.get(intent)
