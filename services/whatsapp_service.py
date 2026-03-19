"""
TaskMate AI - WhatsApp Service
Handles Twilio WhatsApp message sending and webhook processing.
"""

from twilio.rest import Client
from twilio.request_validator import RequestValidator
from typing import Optional
from config import Config


class WhatsAppService:
    """Twilio WhatsApp messaging service."""

    def __init__(self):
        self.account_sid = Config.TWILIO_ACCOUNT_SID
        self.auth_token = Config.TWILIO_AUTH_TOKEN
        self.from_number = Config.TWILIO_WHATSAPP_NUMBER
        
        # Disable if keys are empty or still the default placeholders
        is_placeholder = lambda x: not x or "your-" in x.lower() or "paste-" in x.lower()
        self.enabled = not (is_placeholder(self.account_sid) or is_placeholder(self.auth_token))

        self.client = None
        self.validator = None

        if self.enabled:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                self.validator = RequestValidator(self.auth_token)
            except Exception as e:
                print(f"[WhatsApp Init Error] {e}")
                self.enabled = False

    def send_message(self, to: str, body: str) -> Optional[str]:
        """Send a WhatsApp message via Twilio."""
        if not self.enabled:
            print(f"[WhatsApp Disabled] To: {to} | Message: {body[:100]}...")
            return None

        try:
            # Ensure proper WhatsApp number format
            if not to.startswith("whatsapp:"):
                to = f"whatsapp:{to}"

            message = self.client.messages.create(
                body=body,
                from_=self.from_number,
                to=to
            )

            return message.sid

        except Exception as e:
            print(f"[WhatsApp Error] Failed to send message: {e}")
            return None

    def validate_webhook(self, url: str, params: dict, signature: str) -> bool:
        """Validate that a webhook request came from Twilio."""
        if not self.validator:
            return True  # Skip validation if Twilio not configured

        return self.validator.validate(url, params, signature)

    @staticmethod
    def parse_incoming_message(form_data: dict) -> dict:
        """Parse an incoming Twilio WhatsApp webhook message."""
        return {
            "from": form_data.get("From", ""),
            "to": form_data.get("To", ""),
            "body": form_data.get("Body", "").strip(),
            "message_sid": form_data.get("MessageSid", ""),
            "num_media": int(form_data.get("NumMedia", "0")),
            "profile_name": form_data.get("ProfileName", ""),
            "wa_id": form_data.get("WaId", ""),
        }

    @staticmethod
    def create_twiml_response(message: str) -> str:
        """Create a TwiML response for Twilio webhook."""
        # Escape XML special characters
        message = (
            message
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
        )

        return (
            '<?xml version="1.0" encoding="UTF-8"?>'
            "<Response>"
            f"<Message>{message}</Message>"
            "</Response>"
        )
