"""
TaskMate AI - Utility Helpers
Common helper functions used across the application.
"""

from datetime import datetime


def format_timestamp(iso_string: str) -> str:
    """Format an ISO timestamp to a human-readable string."""
    try:
        dt = datetime.fromisoformat(iso_string)
        return dt.strftime("%I:%M %p, %b %d %Y")
    except (ValueError, TypeError):
        return iso_string


def time_ago(iso_string: str) -> str:
    """Convert an ISO timestamp to a 'time ago' string."""
    try:
        dt = datetime.fromisoformat(iso_string)
        diff = datetime.now() - dt
        seconds = diff.total_seconds()

        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes}m ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours}h ago"
        else:
            days = int(seconds / 86400)
            return f"{days}d ago"
    except (ValueError, TypeError):
        return ""


def truncate(text: str, max_length: int = 100) -> str:
    """Truncate text to a maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def sanitize_phone(phone: str) -> str:
    """Sanitize phone number for consistent storage."""
    return phone.replace("whatsapp:", "").strip()


def mask_phone(phone: str) -> str:
    """Mask phone number for dashboard display."""
    clean = sanitize_phone(phone)
    if len(clean) > 6:
        return clean[:3] + "***" + clean[-3:]
    return clean
