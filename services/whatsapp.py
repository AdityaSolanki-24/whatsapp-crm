import requests
import logging
from typing import Optional
from models.settings import Settings

logger = logging.getLogger(__name__)


class WhatsAppService:
    BASE_URL = "https://graph.facebook.com/v19.0"

    def __init__(self):
        settings = Settings.get_settings()
        self.phone_id = settings.whatsapp_phone_id or ""
        self.access_token = settings.whatsapp_access_token or ""

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def _api_url(self) -> str:
        return f"{self.BASE_URL}/{self.phone_id}/messages"

    def send_text_message(self, to: str, message: str) -> dict:
        """Send a plain text WhatsApp message."""
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {"preview_url": False, "body": message},
        }
        return self._post(payload)

    def send_image_message(self, to: str, image_url: str, caption: str = "") -> dict:
        """Send an image WhatsApp message with optional caption."""
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "image",
            "image": {"link": image_url, "caption": caption},
        }
        return self._post(payload)

    def _post(self, payload: dict) -> dict:
        """Make POST request to WhatsApp API."""
        if not self.phone_id or not self.access_token:
            return {
                "success": False,
                "error": "WhatsApp credentials not configured. Go to Settings.",
            }
        try:
            response = requests.post(
                self._api_url(),
                json=payload,
                headers=self._headers(),
                timeout=30,
            )
            data = response.json()
            if response.status_code == 200 and "messages" in data:
                return {"success": True, "message_id": data["messages"][0].get("id", "")}
            else:
                error_msg = data.get("error", {}).get("message", "Unknown API error")
                logger.error(f"WhatsApp API error: {error_msg} | payload: {payload}")
                return {"success": False, "error": error_msg}
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Request timed out"}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "Connection error to WhatsApp API"}
        except Exception as e:
            logger.exception(f"Unexpected WhatsApp error: {e}")
            return {"success": False, "error": str(e)}

    def test_connection(self) -> dict:
        """Test credentials by calling the phone number info endpoint."""
        if not self.phone_id or not self.access_token:
            return {"success": False, "error": "Credentials not configured"}
        try:
            url = f"{self.BASE_URL}/{self.phone_id}"
            response = requests.get(url, headers=self._headers(), timeout=15)
            data = response.json()
            if response.status_code == 200:
                return {"success": True, "data": data}
            else:
                error_msg = data.get("error", {}).get("message", "Invalid credentials")
                return {"success": False, "error": error_msg}
        except Exception as e:
            return {"success": False, "error": str(e)}
