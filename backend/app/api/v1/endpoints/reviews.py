from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from uuid import UUID

from app.core.database import get_db
from app.models.models import Review, Order

router = APIRouter()

class ReviewCreate(BaseModel):
    order_id: UUID
    rating: int
    comment: str = ""

@router.post("/", status_code=status.HTTP_201_CREATED)
async def submit_review(payload: ReviewCreate, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Order).filter(Order.id == payload.order_id))
    order = res.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    new_review = Review(
        restaurant_id=order.restaurant_id,
        order_id=order.id,
        customer_id=order.customer_id,
        rating=payload.rating,
        comment=payload.comment
    )
    db.add(new_review)
    await db.commit()
    return {"message": "Thank you for your rating!", "rating": payload.rating}
