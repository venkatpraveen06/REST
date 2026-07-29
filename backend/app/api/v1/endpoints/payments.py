from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.models.models import Order, Payment, Customer
from app.services.razorpay_service import razorpay_service
from app.services.stripe_service import stripe_service
from app.services.whatsapp_service import whatsapp_service

router = APIRouter()

@router.post("/generate-link")
async def generate_payment_link(order_id: UUID, gateway: str = "razorpay", db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Order).filter(Order.id == order_id))
    order = res.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    cust_res = await db.execute(select(Customer).filter(Customer.id == order.customer_id))
    customer = cust_res.scalars().first()

    customer_name = customer.name if customer else "Customer"
    customer_phone = customer.whatsapp_number if customer else "+919876543210"

    payment_url = ""
    link_id = ""

    if gateway == "razorpay":
        pay_res = await razorpay_service.create_payment_link(
            order_number=order.order_number,
            amount=float(order.total_amount),
            customer_name=customer_name,
            customer_phone=customer_phone
        )
        payment_url = pay_res.get("short_url")
        link_id = pay_res.get("id")
    else:
        pay_res = await stripe_service.create_checkout_session(
            order_number=order.order_number,
            amount=float(order.total_amount)
        )
        payment_url = pay_res.get("url")
        link_id = pay_res.get("id")

    # Record Payment in DB
    new_payment = Payment(
        restaurant_id=order.restaurant_id,
        order_id=order.id,
        gateway=gateway,
        payment_link_id=link_id,
        payment_link_url=payment_url,
        amount=order.total_amount,
        status="pending"
    )
    db.add(new_payment)
    await db.commit()

    # Send Link on WhatsApp
    if customer_phone:
        await whatsapp_service.send_payment_cta(
            to_phone=customer_phone,
            body_text=f"💳 *Payment Link Generated for Order #{order.order_number}*\n\nTotal Amount: ₹{order.total_amount}",
            payment_url=payment_url
        )

    return {
        "order_id": str(order.id),
        "order_number": order.order_number,
        "payment_url": payment_url,
        "amount": float(order.total_amount)
    }

@router.post("/webhook/razorpay")
async def razorpay_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.json()
    event = payload.get("event")

    if event == "payment_link.paid" or event == "payment.captured":
        entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
        order_num = entity.get("description", "").replace("AuraDine Order #", "").strip()

        # Find order
        res = await db.execute(select(Order).filter(Order.order_number == order_num))
        order = res.scalars().first()
        if order:
            order.status = "confirmed"
            
            # Update Payment status
            p_res = await db.execute(select(Payment).filter(Payment.order_id == order.id))
            payment = p_res.scalars().first()
            if payment:
                payment.status = "captured"
                payment.paid_at = datetime.utcnow()
            
            await db.commit()

            # Send Receipt via WhatsApp
            cust_res = await db.execute(select(Customer).filter(Customer.id == order.customer_id))
            customer = cust_res.scalars().first()
            if customer:
                await whatsapp_service.send_text_message(
                    customer.whatsapp_number,
                    f"✅ *Payment Received!* Your Order #{order.order_number} is confirmed and sent to the kitchen."
                )

    return {"status": "ok"}
