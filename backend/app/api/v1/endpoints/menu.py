from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user_claims
from app.models.models import Category, MenuItem
from app.schemas.schemas import CategoryCreate, CategoryOut, MenuItemCreate, MenuItemOut

router = APIRouter()

# --- CATEGORIES ---
@router.get("/categories", response_model=List[CategoryOut])
async def list_categories(claims: dict = Depends(get_current_user_claims), db: AsyncSession = Depends(get_db)):
    restaurant_id = claims.get("restaurant_id")
    result = await db.execute(select(Category).filter(Category.restaurant_id == UUID(restaurant_id)).order_by(Category.display_order))
    return result.scalars().all()

@router.post("/categories", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
async def create_category(payload: CategoryCreate, claims: dict = Depends(get_current_user_claims), db: AsyncSession = Depends(get_db)):
    restaurant_id = claims.get("restaurant_id")
    slug = payload.name.lower().replace(" ", "-")
    
    new_cat = Category(
        restaurant_id=UUID(restaurant_id),
        name=payload.name,
        slug=slug,
        description=payload.description,
        display_order=payload.display_order
    )
    db.add(new_cat)
    await db.commit()
    await db.refresh(new_cat)
    return new_cat

# --- MENU ITEMS ---
@router.get("/items", response_model=List[MenuItemOut])
async def list_menu_items(claims: dict = Depends(get_current_user_claims), db: AsyncSession = Depends(get_db)):
    restaurant_id = claims.get("restaurant_id")
    result = await db.execute(select(MenuItem).filter(MenuItem.restaurant_id == UUID(restaurant_id)).order_by(MenuItem.name))
    return result.scalars().all()

@router.post("/items", response_model=MenuItemOut, status_code=status.HTTP_201_CREATED)
async def create_menu_item(payload: MenuItemCreate, claims: dict = Depends(get_current_user_claims), db: AsyncSession = Depends(get_db)):
    restaurant_id = claims.get("restaurant_id")
    slug = payload.name.lower().replace(" ", "-")

    new_item = MenuItem(
        restaurant_id=UUID(restaurant_id),
        category_id=payload.category_id,
        name=payload.name,
        slug=slug,
        description=payload.description,
        price=payload.price,
        dietary_type=payload.dietary_type,
        spice_level=payload.spice_level,
        preparation_time_minutes=payload.preparation_time_minutes,
        is_special=payload.is_special,
        is_bestseller=payload.is_bestseller,
        image_url=payload.image_url
    )
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)
    return new_item

@router.patch("/items/{item_id}/toggle-availability")
async def toggle_item_availability(item_id: UUID, claims: dict = Depends(get_current_user_claims), db: AsyncSession = Depends(get_db)):
    restaurant_id = claims.get("restaurant_id")
    result = await db.execute(select(MenuItem).filter(MenuItem.id == item_id, MenuItem.restaurant_id == UUID(restaurant_id)))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    item.is_available = not item.is_available
    await db.commit()
    return {"id": str(item.id), "is_available": item.is_available}
