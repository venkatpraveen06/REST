from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user_claims
from app.models.models import Ingredient

router = APIRouter()

@router.get("/ingredients")
async def list_ingredients(claims: dict = Depends(get_current_user_claims), db: AsyncSession = Depends(get_db)):
    restaurant_id = claims.get("restaurant_id")
    res = await db.execute(select(Ingredient).filter(Ingredient.restaurant_id == UUID(restaurant_id)))
    return res.scalars().all()
