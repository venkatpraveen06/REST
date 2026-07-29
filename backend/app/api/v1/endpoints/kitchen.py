from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user_claims
from app.models.models import Restaurant, Order
from app.schemas.schemas import OrderOut

router = APIRouter()

@router.get("/queue", response_model=List[OrderOut])
async def get_kitchen_queue(claims: dict = Depends(get_current_user_claims), db: AsyncSession = Depends(get_db)):
    """Fetch active orders for Kitchen Display System (KDS)."""
    restaurant_id = claims.get("restaurant_id") if claims else None
    if not restaurant_id:
        r_res = await db.execute(select(Restaurant).limit(1))
        default_rest = r_res.scalars().first()
        rest_uuid = default_rest.id if default_rest else UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")
    else:
        rest_uuid = UUID(restaurant_id)

    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items))
        .filter(
            Order.restaurant_id == rest_uuid,
            Order.status.in_(["pending", "confirmed", "preparing", "ready"])
        )
        .order_by(Order.created_at.asc())
    )

from fastapi import Query, Body
from app.services.whatsapp_service import whatsapp_service

@router.patch("/tickets/{ticket_id}/status")
async def patch_kitchen_ticket_status(
    ticket_id: str,
    new_status: str = Query(None),
    body: dict = Body(None),
    claims: dict = Depends(get_current_user_claims),
    db: AsyncSession = Depends(get_db)
):
    target_status = new_status or (body.get("status") if body else None)
    if not target_status:
        raise HTTPException(status_code=400, detail="Missing status parameter")

    # Flexible Order Lookup
    order = None
    try:
        order_uuid = UUID(ticket_id)
        res = await db.execute(select(Order).options(selectinload(Order.customer)).filter(Order.id == order_uuid))
        order = res.scalars().first()
    except Exception:
        pass

    if not order:
        res = await db.execute(select(Order).options(selectinload(Order.customer)).filter(Order.order_number.ilike(f"%{ticket_id}%")))
        order = res.scalars().first()

    if not order:
        raise HTTPException(status_code=404, detail=f"Ticket '{ticket_id}' not found")

    order.status = target_status.lower()
    await db.commit()

    # WhatsApp Notification Dispatch
    if order.customer and order.customer.whatsapp_number:
        status_messages = {
            "preparing": f"🍳 Order #{order.order_number} is now being PREPARED in the kitchen!",
            "ready": f"🔔 Order #{order.order_number} is READY for pickup/delivery!",
            "delivered": f"🎉 Order #{order.order_number} DELIVERED! Enjoy your meal 🍽️"
        }
        if target_status.lower() in status_messages:
            try:
                await whatsapp_service.send_text_message(order.customer.whatsapp_number, status_messages[target_status.lower()])
            except Exception as e:
                pass

    return {"id": str(order.id), "order_number": order.order_number, "status": order.status}

