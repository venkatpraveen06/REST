from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    restaurants,
    menu,
    orders,
    payments,
    whatsapp,
    ai,
    analytics,
    kitchen,
    customers,
    reviews,
    inventory
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(restaurants.router, prefix="/restaurants", tags=["Restaurants"])
api_router.include_router(menu.router, prefix="/menu", tags=["Menu & Categories"])
api_router.include_router(orders.router, prefix="/orders", tags=["Orders"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
api_router.include_router(whatsapp.router, prefix="/whatsapp", tags=["WhatsApp Automation"])
api_router.include_router(ai.router, prefix="/ai", tags=["Gemini AI Engine"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics & Reports"])
api_router.include_router(kitchen.router, prefix="/kitchen", tags=["Kitchen Display System"])
api_router.include_router(customers.router, prefix="/customers", tags=["Customer CRM"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["Reviews & Ratings"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["Inventory & Ingredients"])
