from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user_claims
from app.models.models import Order
from app.schemas.schemas import OrderOut

router = APIRouter()

@router.get("/queue", response_model=List[OrderOut])
async def get_kitchen_queue(claims: dict = Depends(get_current_user_claims), db: AsyncSession = Depends(get_db)):
    """Fetch active orders for Kitchen Display System (KDS)."""
    restaurant_id = claims.get("restaurant_id")
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items))
        .filter(
            Order.restaurant_id == UUID(restaurant_id),
            Order.status.in_(["pending", "confirmed", "preparing", "ready"])
        )
        .order_by(Order.created_at.asc())
    )
    return result.scalars().all()
