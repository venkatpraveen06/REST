from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Dict, Any
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user_claims
from app.models.models import Customer, Restaurant

router = APIRouter()

@router.get("/")
async def list_customers(claims: dict = Depends(get_current_user_claims), db: AsyncSession = Depends(get_db)):
    restaurant_id = claims.get("restaurant_id") if claims else None
    if not restaurant_id:
        r_res = await db.execute(select(Restaurant).limit(1))
        default_rest = r_res.scalars().first()
        rest_uuid = default_rest.id if default_rest else UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")
    else:
        rest_uuid = UUID(restaurant_id)

    res = await db.execute(select(Customer).filter(Customer.restaurant_id == rest_uuid).order_by(Customer.created_at.desc()))
    return res.scalars().all()

