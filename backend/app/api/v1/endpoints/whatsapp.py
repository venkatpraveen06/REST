from fastapi import APIRouter, Request, Query, Response, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import logging
from uuid import UUID

from app.core.config import settings
from app.core.database import get_db
from app.models.models import Restaurant, MenuItem
from app.services.gemini_service import gemini_service
from app.services.whatsapp_service import whatsapp_service

logger = logging.getLogger("whatsapp_webhook")
router = APIRouter()

@router.get("/webhook")
async def verify_whatsapp_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    """Meta WhatsApp Webhook Verification Challenge Endpoint."""
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        logger.info("WhatsApp Webhook verified successfully.")
        return Response(content=hub_challenge, media_type="text/plain")
    logger.warning("WhatsApp Webhook verification failed.")
    return Response(content="Verification failed", status_code=403)

@router.post("/webhook")
async def receive_whatsapp_message(request: Request, db: AsyncSession = Depends(get_db)):
    """Receives incoming messages from Meta WhatsApp API."""
    body = await request.json()
    logger.info(f"Incoming WhatsApp Payload: {body}")

    try:
        entries = body.get("entry", [])
        for entry in entries:
            changes = entry.get("changes", [])
            for change in changes:
                value = change.get("value", {})
                messages = value.get("messages", [])
                
                if not messages:
                    continue

                msg = messages[0]
                from_phone = msg.get("from")
                msg_type = msg.get("type")
                user_text = ""

                if msg_type == "text":
                    user_text = msg.get("text", {}).get("body", "")
                elif msg_type == "interactive":
                    interactive = msg.get("interactive", {})
                    if interactive.get("type") == "button_reply":
                        user_text = interactive.get("button_reply", {}).get("title", "")
                    elif interactive.get("type") == "list_reply":
                        user_text = interactive.get("list_reply", {}).get("title", "")

                if not user_text or not from_phone:
                    continue

                # Fetch Default / Demo Restaurant Menu
                res = await db.execute(select(Restaurant).limit(1))
                restaurant = res.scalars().first()
                restaurant_id = restaurant.id if restaurant else UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")
                restaurant_name = restaurant.name if restaurant else "Aura Bistro"

                # Fetch Menu Items
                m_res = await db.execute(select(MenuItem).filter(MenuItem.restaurant_id == restaurant_id, MenuItem.is_available == True))
                items = m_res.scalars().all()
                menu_summary = [{"id": str(i.id), "name": i.name, "price": float(i.price), "dietary": i.dietary_type} for i in items]

                # Pass to Gemini AI Service
                ai_response = await gemini_service.parse_whatsapp_message(
                    user_message=user_text,
                    restaurant_name=restaurant_name,
                    menu_items_summary=menu_summary
                )

                reply_text = ai_response.get("reply_text", "How can I help you today?")
                buttons = ai_response.get("interactive_buttons", [])

                if buttons:
                    await whatsapp_service.send_button_message(
                        to_phone=from_phone,
                        header_text=restaurant_name,
                        body_text=reply_text,
                        buttons=buttons
                    )
                else:
                    await whatsapp_service.send_text_message(from_phone, reply_text)

    except Exception as e:
        logger.error(f"Error handling WhatsApp webhook: {e}")

    return {"status": "event_received"}
