from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user_claims
from app.models.models import Restaurant, RestaurantSettings
from app.schemas.schemas import RestaurantOut

router = APIRouter()

@router.get("/me", response_model=RestaurantOut)
async def get_current_restaurant(claims: dict = Depends(get_current_user_claims), db: AsyncSession = Depends(get_db)):
    restaurant_id = claims.get("restaurant_id")
    if not restaurant_id:
        raise HTTPException(status_code=400, detail="User is not associated with any restaurant")

    result = await db.execute(select(Restaurant).filter(Restaurant.id == UUID(restaurant_id)))
    restaurant = result.scalars().first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    return restaurant

@router.get("/settings")
async def get_restaurant_settings(claims: dict = Depends(get_current_user_claims), db: AsyncSession = Depends(get_db)):
    restaurant_id = claims.get("restaurant_id")
    if not restaurant_id:
        raise HTTPException(status_code=400, detail="No restaurant found in claims")

    result = await db.execute(select(RestaurantSettings).filter(RestaurantSettings.restaurant_id == UUID(restaurant_id)))
    settings = result.scalars().first()
    return settings or {}
