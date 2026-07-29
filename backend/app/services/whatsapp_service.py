import httpx
import logging
from typing import Dict, Any, List, Optional
from app.core.config import settings

logger = logging.getLogger("whatsapp_service")

class WhatsAppService:
    def __init__(self):
        self.access_token = settings.WHATSAPP_TOKEN
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.api_url = f"https://graph.facebook.com/v19.0/{self.phone_number_id}/messages"

    async def send_text_message(self, to_phone: str, message: str) -> Dict[str, Any]:
        """Sends simple text message via WhatsApp Cloud API."""
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_phone,
            "type": "text",
            "text": {"preview_url": False, "body": message}
        }
        return await self._send_request(payload)

    async def send_button_message(self, to_phone: str, header_text: str, body_text: str, buttons: List[Dict[str, str]]) -> Dict[str, Any]:
        """Sends interactive button message (up to 3 buttons)."""
        formatted_buttons = []
        for btn in buttons[:3]:
            formatted_buttons.append({
                "type": "reply",
                "reply": {
                    "id": btn.get("id", "btn_action"),
                    "title": btn.get("title", "Select")[:20]
                }
            })

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_phone,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "header": {"type": "text", "text": header_text},
                "body": {"text": body_text},
                "action": {"buttons": formatted_buttons}
            }
        }
        return await self._send_request(payload)

    async def send_list_message(self, to_phone: str, header_text: str, body_text: str, button_label: str, sections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Sends interactive list message (categories, menu selection)."""
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_phone,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {"type": "text", "text": header_text},
                "body": {"text": body_text},
                "action": {
                    "button": button_label[:20],
                    "sections": sections
                }
            }
        }
        return await self._send_request(payload)

    async def send_payment_cta(self, to_phone: str, body_text: str, payment_url: str, link_title: str = "Pay Now 💳") -> Dict[str, Any]:
        """Sends CTA link message for payment links."""
        message_with_link = f"{body_text}\n\n👉 *Click here to complete payment:*\n{payment_url}"
        return await self.send_button_message(
            to_phone=to_phone,
            header_text="Secure Checkout",
            body_text=message_with_link,
            buttons=[{"id": "btn_paid", "title": "I've Paid ✅"}, {"id": "btn_cancel", "title": "Cancel Order ❌"}]
        )

    async def _send_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.api_url, json=payload, headers=headers, timeout=10.0)
                res_data = response.json()
                logger.info(f"WhatsApp API Response: {res_data}")
                return res_data
            except Exception as e:
                logger.error(f"WhatsApp API HTTP Error: {e}")
                return {"error": str(e)}

whatsapp_service = WhatsAppService()
