from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import uuid

from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.models import User, Restaurant, RestaurantSettings
from app.schemas.schemas import UserRegister, UserLogin, Token, UserOut

router = APIRouter()

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register_restaurant_owner(payload: UserRegister, db: AsyncSession = Depends(get_db)):
    # Check if email exists
    result = await db.execute(select(User).filter(User.email == payload.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create Restaurant Tenant
    slug_base = payload.restaurant_name.lower().replace(" ", "-")
    restaurant_slug = f"{slug_base}-{str(uuid.uuid4())[:4]}"
    
    new_restaurant = Restaurant(
        name=payload.restaurant_name,
        slug=restaurant_slug,
        phone_number=payload.phone_number
    )
    db.add(new_restaurant)
    await db.flush() # Flush to populate new_restaurant.id

    # Create Settings
    new_settings = RestaurantSettings(restaurant_id=new_restaurant.id)
    db.add(new_settings)

    # Create Owner User
    hashed_pwd = get_password_hash(payload.password)
    new_user = User(
        email=payload.email,
        password_hash=hashed_pwd,
        full_name=payload.full_name,
        phone_number=payload.phone_number,
        role="restaurant_owner",
        restaurant_id=new_restaurant.id
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Generate JWT
    token = create_access_token(
        subject=str(new_user.id),
        restaurant_id=str(new_restaurant.id),
        role=new_user.role
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(new_user.id),
            "email": new_user.email,
            "full_name": new_user.full_name,
            "role": new_user.role,
            "restaurant_id": str(new_restaurant.id),
            "restaurant_name": new_restaurant.name
        }
    }

@router.post("/login", response_model=Token)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.email == payload.email))
    user = result.scalars().first()
    
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Get restaurant details
    restaurant_name = ""
    if user.restaurant_id:
        res = await db.execute(select(Restaurant).filter(Restaurant.id == user.restaurant_id))
        restaurant = res.scalars().first()
        if restaurant:
            restaurant_name = restaurant.name

    token = create_access_token(
        subject=str(user.id),
        restaurant_id=str(user.restaurant_id) if user.restaurant_id else None,
        role=user.role
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "restaurant_id": str(user.restaurant_id) if user.restaurant_id else None,
            "restaurant_name": restaurant_name
        }
    }
