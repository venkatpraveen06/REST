from typing import Optional, List, Any, Dict
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, time
from uuid import UUID

# User & Auth Schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone_number: str
    restaurant_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    role: str
    restaurant_id: Optional[UUID]
    
    class Config:
        from_attributes = True

# Restaurant Schemas
class RestaurantBase(BaseModel):
    name: str
    slug: str
    phone_number: str
    currency: str = "INR"
    currency_symbol: str = "₹"

class RestaurantOut(RestaurantBase):
    id: UUID
    logo_url: Optional[str]
    rating: float
    review_count: int
    is_active: bool
    
    class Config:
        from_attributes = True

# Category Schemas
class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    display_order: int = 0

class CategoryOut(CategoryCreate):
    id: UUID
    slug: str
    is_available: bool
    
    class Config:
        from_attributes = True

# Menu Item Schemas
class MenuItemCreate(BaseModel):
    category_id: UUID
    name: str
    description: Optional[str] = None
    price: float
    dietary_type: str = "veg"
    spice_level: str = "medium"
    preparation_time_minutes: int = 15
    is_special: bool = False
    is_bestseller: bool = False
    image_url: Optional[str] = None

class MenuItemOut(MenuItemCreate):
    id: UUID
    slug: str
    is_available: bool
    
    class Config:
        from_attributes = True

# Order Schemas
class CartItemInput(BaseModel):
    menu_item_id: UUID
    quantity: int
    special_notes: Optional[str] = None

class OrderCreateInput(BaseModel):
    restaurant_id: UUID
    customer_whatsapp: str
    customer_name: Optional[str] = None
    order_type: str = "delivery"
    delivery_address: Optional[str] = None
    items: List[CartItemInput]
    special_instructions: Optional[str] = None

class OrderItemOut(BaseModel):
    id: UUID
    item_name: str
    quantity: int
    unit_price: float
    total_price: float
    special_notes: Optional[str]

class OrderOut(BaseModel):
    id: UUID
    order_number: str
    status: str
    order_type: str
    delivery_address: Optional[str]
    subtotal: float
    tax_amount: float
    delivery_fee: float
    packing_charge: float
    total_amount: float
    special_instructions: Optional[str]
    items: List[OrderItemOut] = []
    
    class Config:
        from_attributes = True


# AI Schemas
class AIIntentRequest(BaseModel):
    restaurant_id: UUID
    customer_whatsapp: str
    user_message: str

class AIIntentResponse(BaseModel):
    intent: str # welcome, view_menu, place_order, track_order, recommendation, unknown
    reply_text: str
    cart: List[Dict[str, Any]] = []
    payment_link: Optional[str] = None
    interactive_buttons: Optional[List[Dict[str, str]]] = None

# Analytics Schemas
class DashboardStatsOut(BaseModel):
    today_revenue: float
    today_orders_count: int
    pending_orders_count: int
    completed_orders_count: int
    popular_items: List[Dict[str, Any]]
    recent_orders: List[OrderOut]
