"""
TaskMate AI - Intent Detection System
Detects user intent from natural language input using keyword matching + GPT classification.
"""

import re
from typing import Dict, Tuple, Optional
from datetime import datetime, timedelta


# Intent categories
INTENTS = {
    "reminder": "User wants to set a reminder or alarm",
    "task_create": "User wants to create a task or to-do item",
    "task_complete": "User wants to mark a task as done",
    "task_list": "User wants to see their tasks",
    "summarize": "User wants to summarize text or notes",
    "weather": "User wants weather information",
    "help": "User wants to know what the bot can do",
    "greeting": "User is greeting or saying hello",
    "general": "General conversation or question"
}

# Keyword patterns for each intent
INTENT_PATTERNS = {
    "reminder": [
        r"remind\s*(me)?", r"reminder", r"set\s*(a)?\s*remind",
        r"alarm", r"notify\s*(me)?", r"don'?t\s*forget",
        r"alert\s*(me)?", r"remember\s*to", r"wake\s*(me)?\s*up"
    ],
    "task_create": [
        r"add\s*(a)?\s*task", r"create\s*(a)?\s*task", r"new\s*task",
        r"todo", r"to[\s-]?do", r"add\s*to\s*(my)?\s*list",
        r"i\s*need\s*to", r"i\s*have\s*to", r"put\s*on\s*(my)?\s*list"
    ],
    "task_complete": [
        r"complete\s*(task)?", r"done\s*with", r"finished",
        r"mark\s*(as)?\s*(done|complete)", r"check\s*off",
        r"i\s*(did|finished|completed)"
    ],
    "task_list": [
        r"(show|list|view|see|get)\s*(my)?\s*tasks",
        r"what\s*(are)?\s*(my)?\s*tasks", r"pending\s*tasks",
        r"my\s*to[\s-]?do", r"task\s*list"
    ],
    "summarize": [
        r"summarize", r"summary", r"sum\s*up", r"shorten",
        r"brief", r"tldr", r"tl;?dr", r"condense",
        r"make\s*(it)?\s*shorter", r"key\s*points"
    ],
    "weather": [
        r"weather", r"temperature", r"forecast",
        r"is\s*it\s*(raining|sunny|cold|hot|warm)",
        r"rain", r"sun", r"snow", r"climate",
        r"how('?s| is)\s*the\s*weather"
    ],
    "help": [
        r"^help$", r"what\s*can\s*you\s*do", r"how\s*to\s*use",
        r"features", r"commands", r"guide", r"instructions",
        r"what\s*are\s*your\s*(capabilities|features)"
    ],
    "greeting": [
        r"^(hi|hello|hey|hola|sup|yo|greetings)[\s!?.]*$",
        r"good\s*(morning|afternoon|evening|night)",
        r"what'?s\s*up", r"howdy"
    ]
}

# Time extraction patterns
TIME_PATTERNS = [
    (r"in\s*(\d+)\s*min(ute)?s?", "minutes"),
    (r"in\s*(\d+)\s*hour?s?", "hours"),
    (r"in\s*(\d+)\s*day?s?", "days"),
    (r"at\s*(\d{1,2}):?(\d{2})?\s*(am|pm)?", "specific_time"),
    (r"tomorrow\s*(at)?\s*(\d{1,2}):?(\d{2})?\s*(am|pm)?", "tomorrow"),
    (r"tonight", "tonight"),
    (r"this\s*evening", "evening"),
    (r"this\s*afternoon", "afternoon"),
]


def detect_intent(message: str) -> Dict:
    """
    Detect the user's intent from their message.

    Returns:
        dict with keys: intent, confidence, entities
    """
    message_lower = message.lower().strip()

    # Check each intent's patterns
    scores = {}
    for intent, patterns in INTENT_PATTERNS.items():
        score = 0
        for pattern in patterns:
            if re.search(pattern, message_lower):
                score += 1
        if score > 0:
            scores[intent] = score

    # Determine best intent
    if scores:
        best_intent = max(scores, key=scores.get)
        max_score = scores[best_intent]
        total_patterns = len(INTENT_PATTERNS[best_intent])
        confidence = min(max_score / max(total_patterns * 0.3, 1), 1.0)
    else:
        best_intent = "general"
        confidence = 0.5

    # Extract entities
    entities = extract_entities(message, best_intent)

    return {
        "intent": best_intent,
        "confidence": round(confidence, 2),
        "entities": entities,
        "raw_message": message
    }


def extract_entities(message: str, intent: str) -> Dict:
    """Extract relevant entities from the message based on intent."""
    entities = {}
    message_lower = message.lower()

    if intent in ("reminder", "task_create"):
        # Extract time information
        time_info = extract_time(message_lower)
        if time_info:
            entities["time"] = time_info

        # Extract the task/reminder content
        content = extract_action_content(message_lower, intent)
        if content:
            entities["content"] = content

        # Extract priority
        priority = extract_priority(message_lower)
        if priority:
            entities["priority"] = priority

    elif intent == "weather":
        # Extract location
        location = extract_location(message_lower)
        if location:
            entities["location"] = location

    elif intent == "task_complete":
        # Extract task identifier
        content = extract_action_content(message_lower, intent)
        if content:
            entities["task_identifier"] = content

    elif intent == "summarize":
        # The content to summarize
        content = extract_summarize_content(message)
        if content:
            entities["content"] = content

    return entities


def extract_time(message: str) -> Optional[str]:
    """Extract time information from a message and return ISO format datetime."""
    now = datetime.now()

    # Check "in X minutes/hours/days"
    for pattern, unit in TIME_PATTERNS:
        match = re.search(pattern, message)
        if match:
            if unit == "minutes":
                delta = timedelta(minutes=int(match.group(1)))
                return (now + delta).isoformat()
            elif unit == "hours":
                delta = timedelta(hours=int(match.group(1)))
                return (now + delta).isoformat()
            elif unit == "days":
                delta = timedelta(days=int(match.group(1)))
                return (now + delta).isoformat()
            elif unit == "specific_time":
                hour = int(match.group(1))
                minute = int(match.group(2)) if match.group(2) else 0
                period = match.group(3)
                if period and period.lower() == "pm" and hour != 12:
                    hour += 12
                elif period and period.lower() == "am" and hour == 12:
                    hour = 0
                target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if target <= now:
                    target += timedelta(days=1)
                return target.isoformat()
            elif unit == "tomorrow":
                tomorrow = now + timedelta(days=1)
                hour = int(match.group(2)) if match.group(2) else 9
                minute = int(match.group(3)) if match.group(3) else 0
                period = match.group(4)
                if period and period.lower() == "pm" and hour != 12:
                    hour += 12
                target = tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)
                return target.isoformat()
            elif unit == "tonight":
                target = now.replace(hour=21, minute=0, second=0, microsecond=0)
                if target <= now:
                    target += timedelta(days=1)
                return target.isoformat()
            elif unit == "evening":
                target = now.replace(hour=18, minute=0, second=0, microsecond=0)
                if target <= now:
                    target += timedelta(days=1)
                return target.isoformat()
            elif unit == "afternoon":
                target = now.replace(hour=14, minute=0, second=0, microsecond=0)
                if target <= now:
                    target += timedelta(days=1)
                return target.isoformat()

    # Default: 1 hour from now
    return None


def extract_action_content(message: str, intent: str) -> Optional[str]:
    """Extract the main content/subject from a reminder or task message."""
    # Remove common prefixes
    clean_patterns = [
        r"^(please\s+)?remind\s*(me)?\s*(to)?\s*",
        r"^(please\s+)?set\s*(a)?\s*remind(er)?\s*(to|for)?\s*",
        r"^(please\s+)?add\s*(a)?\s*task\s*(to)?\s*",
        r"^(please\s+)?create\s*(a)?\s*task\s*(to|for)?\s*",
        r"^(please\s+)?i\s*need\s*to\s*",
        r"^(please\s+)?i\s*have\s*to\s*",
        r"^(i\s*)?(did|finished|completed)\s*",
        r"^(please\s+)?(mark|check)\s*(off)?\s*",
        r"^done\s*with\s*",
    ]

    content = message
    for pattern in clean_patterns:
        content = re.sub(pattern, "", content, flags=re.IGNORECASE).strip()

    # Remove time references at the end
    time_suffixes = [
        r"\s*(in\s*\d+\s*(min(ute)?s?|hours?|days?))\s*$",
        r"\s*(at\s*\d{1,2}:?\d{0,2}\s*(am|pm)?)\s*$",
        r"\s*(tomorrow(\s*at\s*\d{1,2}:?\d{0,2}\s*(am|pm)?)?)\s*$",
        r"\s*(tonight|this\s*(evening|afternoon))\s*$",
    ]

    for pattern in time_suffixes:
        content = re.sub(pattern, "", content, flags=re.IGNORECASE).strip()

    return content if content else None


def extract_priority(message: str) -> Optional[str]:
    """Extract priority level from message."""
    if re.search(r"\b(urgent|asap|important|critical|high\s*priority)\b", message):
        return "high"
    elif re.search(r"\b(low\s*priority|whenever|no\s*rush|not\s*urgent)\b", message):
        return "low"
    return "medium"


def extract_location(message: str) -> Optional[str]:
    """Extract location from weather-related messages."""
    # Pattern: "weather in LOCATION" or "weather for LOCATION"
    patterns = [
        r"weather\s*(?:in|for|at|of)\s+([a-zA-Z\s]+?)(?:\s*[\?\.]?\s*$)",
        r"(?:in|for|at)\s+([a-zA-Z\s]+?)\s+weather",
        r"temperature\s*(?:in|for|at|of)\s+([a-zA-Z\s]+?)(?:\s*[\?\.]?\s*$)",
    ]
    for pattern in patterns:
        match = re.search(pattern, message)
        if match:
            return match.group(1).strip()
    return None


def extract_summarize_content(message: str) -> Optional[str]:
    """Extract content that needs to be summarized."""
    # Remove the summarize command itself
    clean_patterns = [
        r"^(please\s+)?(summarize|summary|sum\s*up|shorten|condense)\s*(this|the|following)?\s*:?\s*",
        r"^(give\s*(me)?\s*(a)?\s*)?tldr\s*:?\s*",
    ]

    content = message
    for pattern in clean_patterns:
        content = re.sub(pattern, "", content, flags=re.IGNORECASE).strip()

    return content if content and len(content) > 10 else None


def get_gpt_intent_prompt(message: str) -> str:
    """Generate a prompt for GPT-based intent classification as fallback."""
    return f"""Classify the following user message into exactly one intent category.

Categories:
- reminder: User wants to set a reminder
- task_create: User wants to create a task or to-do
- task_complete: User wants to mark a task as done
- task_list: User wants to see their tasks
- summarize: User wants to summarize text
- weather: User wants weather information
- help: User wants to know capabilities
- greeting: User is greeting
- general: General conversation

Message: "{message}"

Respond with ONLY the intent category name, nothing else."""
