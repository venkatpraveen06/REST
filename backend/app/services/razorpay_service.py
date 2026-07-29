import razorpay
import logging
from typing import Dict, Any
from app.core.config import settings

logger = logging.getLogger("razorpay_service")

class RazorpayService:
    def __init__(self):
        self.key_id = settings.RAZORPAY_KEY_ID
        self.key_secret = settings.RAZORPAY_KEY_SECRET
        self.client = None
        if self.key_id and self.key_id != "rzp_test_key":
            try:
                self.client = razorpay.Client(auth=(self.key_id, self.key_secret))
            except Exception as e:
                logger.warning(f"Razorpay Client init failed: {e}")

    async def create_payment_link(
        self,
        order_number: str,
        amount: float,
        customer_name: str,
        customer_phone: str,
        customer_email: str = "customer@auradine.com"
    ) -> Dict[str, Any]:
        """Creates dynamic Razorpay payment link for WhatsApp order."""
        if not self.client:
            # Sandbox / Simulated Payment Link for immediate testing
            mock_link = f"https://rzp.io/i/auradine_simulated_{order_number}"
            return {
                "id": f"plink_mock_{order_number}",
                "short_url": mock_link,
                "status": "created",
                "amount": int(amount * 100)
            }

        try:
            payment_link_data = {
                "amount": int(amount * 100), # amount in paise
                "currency": "INR",
                "accept_partial": False,
                "reference_id": order_number,
                "description": f"AuraDine Order #{order_number}",
                "customer": {
                    "name": customer_name,
                    "contact": customer_phone,
                    "email": customer_email
                },
                "notify": {"sms": False, "email": False},
                "reminder_enable": True,
                "callback_url": "https://auradine.com/payment/success",
                "callback_method": "get"
            }
            res = self.client.payment_link.create(payment_link_data)
            return res
        except Exception as e:
            logger.error(f"Razorpay link creation failed: {e}")
            return {
                "id": f"plink_fallback_{order_number}",
                "short_url": f"https://rzp.io/i/auradine_{order_number}",
                "status": "created"
            }

    def verify_webhook_signature(self, body: str, signature: str, secret: str) -> bool:
        """Verifies Razorpay Webhook signature."""
        try:
            self.client.utility.verify_webhook_signature(body, signature, secret)
            return True
        except Exception:
            return False

razorpay_service = RazorpayService()
