from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Dict, Any
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user_claims
from app.models.models import Customer

router = APIRouter()

@router.get("/")
async def list_customers(claims: dict = Depends(get_current_user_claims), db: AsyncSession = Depends(get_db)):
    restaurant_id = claims.get("restaurant_id")
    res = await db.execute(select(Customer).filter(Customer.restaurant_id == UUID(restaurant_id)).order_by(Customer.created_at.desc()))
    return res.scalars().all()
