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

from app.models.models import Restaurant, MenuItem, Customer, Order, OrderItem
import random
from datetime import datetime
from sqlalchemy.orm import selectinload

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
    """Receives incoming messages from Meta WhatsApp API and creates real DB orders."""
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

                # Fetch Default Restaurant
                res = await db.execute(select(Restaurant).limit(1))
                restaurant = res.scalars().first()
                if not restaurant:
                    continue
                restaurant_id = restaurant.id
                restaurant_name = restaurant.name

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
                detected_items = ai_response.get("detected_items", [])
                buttons = ai_response.get("interactive_buttons", [])
                intent = ai_response.get("intent", "")

                # IF ORDER DETECTED OR CONFIRMED -> SAVE REAL ORDER TO POSTGRESQL DATABASE
                if detected_items or "confirm" in user_text.lower() or "pay" in user_text.lower() or intent == "place_order":
                    # 1. Find or create Customer
                    c_res = await db.execute(select(Customer).filter(
                        Customer.restaurant_id == restaurant_id,
                        Customer.whatsapp_number == from_phone
                    ))
                    customer = c_res.scalars().first()
                    if not customer:
                        customer = Customer(
                            restaurant_id=restaurant_id,
                            whatsapp_number=from_phone,
                            name=f"WhatsApp Customer (+{from_phone[-4:]})"
                        )
                        db.add(customer)
                        await db.flush()

                    # 2. Build Order Items & Totals
                    if not detected_items and items:
                        # Fallback default item if none explicitly parsed
                        first_item = items[0]
                        detected_items = [{
                            "item_id": str(first_item.id),
                            "item_name": first_item.name,
                            "quantity": 1,
                            "unit_price": float(first_item.price),
                            "special_notes": None
                        }]

                    subtotal = 0.0
                    order_items_list = []
                    for item_data in detected_items:
                        item_price = float(item_data.get("unit_price", 250.0))
                        item_qty = int(item_data.get("quantity", 1))
                        item_total = item_price * item_qty
                        subtotal += item_total
                        
                        m_id = item_data.get("item_id")
                        menu_item_uuid = UUID(m_id) if m_id else items[0].id

                        order_items_list.append(OrderItem(
                            menu_item_id=menu_item_uuid,
                            item_name=item_data.get("item_name", "Gourmet Dish"),
                            quantity=item_qty,
                            unit_price=item_price,
                            total_price=item_total,
                            special_notes=item_data.get("special_notes")
                        ))

                    tax_amount = round(subtotal * 0.05, 2)
                    packing_charge = 15.0
                    delivery_fee = 30.0
                    total_amount = round(subtotal + tax_amount + packing_charge + delivery_fee, 2)
                    order_num = f"ORD-{datetime.utcnow().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

                    new_order = Order(
                        restaurant_id=restaurant_id,
                        customer_id=customer.id,
                        order_number=order_num,
                        status="pending",
                        order_type="delivery",
                        subtotal=subtotal,
                        tax_amount=tax_amount,
                        delivery_fee=delivery_fee,
                        packing_charge=packing_charge,
                        total_amount=total_amount,
                        special_instructions="Created via WhatsApp AI",
                        items=order_items_list
                    )

                    db.add(new_order)
                    await db.commit()
                    logger.info(f"SUCCESSFULLY CREATED DB ORDER: {order_num} for customer {from_phone}")

                    reply_text = f"🎉 Order Confirmed! #{order_num}\n\n" + \
                                 f"🛒 Total: ₹{total_amount:.2f} (Pay at Counter / COD)\n" + \
                                 f"🍳 Status: Sent live to Kitchen KDS!\n" + \
                                 f"Estimated prep time: 20 minutes."
                    buttons = [
                        {"id": "track_order", "title": "📍 Track Order"}
                    ]

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

