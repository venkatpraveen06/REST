import stripe
import logging
from typing import Dict, Any
from app.core.config import settings

logger = logging.getLogger("stripe_service")

class StripeService:
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY

    async def create_checkout_session(
        self,
        order_number: str,
        amount: float,
        currency: str = "usd"
    ) -> Dict[str, Any]:
        """Creates dynamic Stripe Checkout session."""
        if not settings.STRIPE_SECRET_KEY or settings.STRIPE_SECRET_KEY == "sk_test_123":
            return {
                "id": f"cs_mock_{order_number}",
                "url": f"https://checkout.stripe.com/pay/mock_{order_number}"
            }

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": currency,
                        "product_data": {
                            "name": f"AuraDine Order #{order_number}",
                        },
                        "unit_amount": int(amount * 100),
                    },
                    "quantity": 1,
                }],
                mode="payment",
                client_reference_id=order_number,
                success_url="https://auradine.com/success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url="https://auradine.com/cancel",
            )
            return {"id": session.id, "url": session.url}
        except Exception as e:
            logger.error(f"Stripe Checkout creation failed: {e}")
            return {"id": f"cs_err_{order_number}", "url": f"https://checkout.stripe.com/pay/mock_{order_number}"}

stripe_service = StripeService()
