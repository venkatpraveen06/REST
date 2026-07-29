from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List
from uuid import UUID
import random
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user_claims
from app.models.models import Order, OrderItem, Customer, MenuItem, RestaurantSettings, Restaurant
from app.schemas.schemas import OrderCreateInput, OrderOut
from app.services.whatsapp_service import whatsapp_service

router = APIRouter()

@router.get("/", response_model=List[OrderOut])
async def list_orders(status_filter: str = None, claims: dict = Depends(get_current_user_claims), db: AsyncSession = Depends(get_db)):
    restaurant_id = claims.get("restaurant_id") if claims else None
    if not restaurant_id:
        r_res = await db.execute(select(Restaurant).limit(1))
        default_rest = r_res.scalars().first()
        rest_uuid = default_rest.id if default_rest else UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")
    else:
        rest_uuid = UUID(restaurant_id)

    query = select(Order).options(selectinload(Order.items)).filter(Order.restaurant_id == rest_uuid)
    if status_filter:
        query = query.filter(Order.status == status_filter)
    query = query.order_by(Order.created_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/create", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(payload: OrderCreateInput, db: AsyncSession = Depends(get_db)):
    # Find or Create Customer
    res = await db.execute(select(Customer).filter(
        Customer.restaurant_id == payload.restaurant_id,
        Customer.whatsapp_number == payload.customer_whatsapp
    ))
    customer = res.scalars().first()
    if not customer:
        customer = Customer(
            restaurant_id=payload.restaurant_id,
            whatsapp_number=payload.customer_whatsapp,
            name=payload.customer_name or "WhatsApp Customer"
        )
        db.add(customer)
        await db.flush()

    # Calculate Totals
    subtotal = 0.0
    order_items_list = []
    
    for item_input in payload.items:
        m_res = await db.execute(select(MenuItem).filter(MenuItem.id == item_input.menu_item_id))
        menu_item = m_res.scalars().first()
        if not menu_item:
            continue
        
        unit_price = float(menu_item.price)
        total_price = unit_price * item_input.quantity
        subtotal += total_price
        
        order_items_list.append(
            OrderItem(
                menu_item_id=menu_item.id,
                item_name=menu_item.name,
                quantity=item_input.quantity,
                unit_price=unit_price,
                total_price=total_price,
                special_notes=item_input.special_notes
            )
        )

    tax_amount = round(subtotal * 0.05, 2)
    delivery_fee = 30.0 if payload.order_type == "delivery" else 0.0
    packing_charge = 15.0
    total_amount = round(subtotal + tax_amount + delivery_fee + packing_charge, 2)

    order_num = f"ORD-{datetime.utcnow().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

    new_order = Order(
        restaurant_id=payload.restaurant_id,
        customer_id=customer.id,
        order_number=order_num,
        status="pending",
        order_type=payload.order_type,
        delivery_address=payload.delivery_address,
        subtotal=subtotal,
        tax_amount=tax_amount,
        delivery_fee=delivery_fee,
        packing_charge=packing_charge,
        total_amount=total_amount,
        special_instructions=payload.special_instructions,
        items=order_items_list
    )

    db.add(new_order)
    await db.commit()

    # Re-query with items loaded
    result = await db.execute(select(Order).options(selectinload(Order.items)).filter(Order.id == new_order.id))
    return result.scalars().first()

@router.patch("/{order_id}/status")

async def update_order_status(
    order_id: str,
    new_status: str = Query(None),
    body: dict = Body(None),
    claims: dict = Depends(get_current_user_claims),
    db: AsyncSession = Depends(get_db)
):
    target_status = new_status or (body.get("status") if body else None)
    if not target_status:
        raise HTTPException(status_code=400, detail="Missing new_status parameter")

    # Flexible Order Lookup (UUID or Order Number string)
    order = None
    try:
        order_uuid = UUID(order_id)
        res = await db.execute(select(Order).options(selectinload(Order.customer)).filter(Order.id == order_uuid))
        order = res.scalars().first()
    except Exception:
        pass

    if not order:
        res = await db.execute(select(Order).options(selectinload(Order.customer)).filter(Order.order_number.ilike(f"%{order_id}%")))
        order = res.scalars().first()

    if not order:
        raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found")

    order.status = target_status.lower()
    await db.commit()

    # WhatsApp Customer Notification on Status Change
    if order.customer and order.customer.whatsapp_number:
        status_messages = {
            "preparing": f"🍳 Order #{order.order_number} is now being PREPARED in the kitchen!",
            "ready": f"🔔 Order #{order.order_number} is READY for pickup/delivery!",
            "out_for_delivery": f"🛵 Order #{order.order_number} is OUT FOR DELIVERY! Driver is on the way.",
            "delivered": f"🎉 Order #{order.order_number} DELIVERED! Enjoy your meal 🍽️\nHow was your experience? Rate us 1-5 ⭐"
        }
        if target_status.lower() in status_messages:
            try:
                await whatsapp_service.send_text_message(order.customer.whatsapp_number, status_messages[target_status.lower()])
            except Exception as e:
                logger.error(f"WhatsApp notification dispatch error: {e}")

    return {"id": str(order.id), "order_number": order.order_number, "status": order.status}

