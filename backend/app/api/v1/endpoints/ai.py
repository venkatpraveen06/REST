from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID

from app.core.database import get_db
from app.models.models import Restaurant, MenuItem
from app.schemas.schemas import AIIntentRequest, AIIntentResponse
from app.services.gemini_service import gemini_service

router = APIRouter()

@router.post("/parse-intent", response_model=AIIntentResponse)
async def parse_intent(payload: AIIntentRequest, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Restaurant).filter(Restaurant.id == payload.restaurant_id))
    restaurant = res.scalars().first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    m_res = await db.execute(select(MenuItem).filter(MenuItem.restaurant_id == payload.restaurant_id, MenuItem.is_available == True))
    items = m_res.scalars().all()
    menu_summary = [{"id": str(i.id), "name": i.name, "price": float(i.price), "dietary": i.dietary_type} for i in items]

    ai_result = await gemini_service.parse_whatsapp_message(
        user_message=payload.user_message,
        restaurant_name=restaurant.name,
        menu_items_summary=menu_summary
    )

    return {
        "intent": ai_result.get("intent", "unknown"),
        "reply_text": ai_result.get("reply_text", ""),
        "cart": ai_result.get("detected_items", []),
        "interactive_buttons": ai_result.get("interactive_buttons", [])
    }
