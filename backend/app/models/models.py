import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Numeric, Integer, Text, Time, DateTime, ForeignKey, Enum as SQLEnum, JSON, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from app.core.database import Base

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    logo_url = Column(Text, nullable=True)
    banner_url = Column(Text, nullable=True)
    phone_number = Column(String(50), unique=True, nullable=False)
    whatsapp_phone_number_id = Column(String(100), nullable=True)
    whatsapp_waba_id = Column(String(100), nullable=True)
    whatsapp_access_token = Column(Text, nullable=True)
    currency = Column(String(10), default="INR")
    currency_symbol = Column(String(5), default="₹")
    timezone = Column(String(50), default="Asia/Kolkata")
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    rating = Column(Numeric(3, 2), default=5.00)
    review_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    settings = relationship("RestaurantSettings", back_populates="restaurant", uselist=False, cascade="all, delete-orphan")
    users = relationship("User", back_populates="restaurant", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="restaurant", cascade="all, delete-orphan")
    menu_items = relationship("MenuItem", back_populates="restaurant", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="restaurant", cascade="all, delete-orphan")
    customers = relationship("Customer", back_populates="restaurant", cascade="all, delete-orphan")


class RestaurantSettings(Base):
    __tablename__ = "restaurant_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), unique=True, nullable=False)
    auto_accept_orders = Column(Boolean, default=False)
    tax_percentage = Column(Numeric(5, 2), default=5.00)
    packing_charge = Column(Numeric(10, 2), default=10.00)
    delivery_fee_per_km = Column(Numeric(10, 2), default=15.00)
    min_order_amount = Column(Numeric(10, 2), default=100.00)
    free_delivery_above = Column(Numeric(10, 2), default=500.00)
    opening_time = Column(Time, default="10:00:00")
    closing_time = Column(Time, default="23:00:00")
    razorpay_key_id = Column(Text, nullable=True)
    razorpay_key_secret = Column(Text, nullable=True)
    stripe_publishable_key = Column(Text, nullable=True)
    stripe_secret_key = Column(Text, nullable=True)
    gemini_custom_prompt = Column(Text, nullable=True)
    loyalty_points_ratio = Column(Numeric(5, 2), default=0.05)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    restaurant = relationship("Restaurant", back_populates="settings")


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supabase_auth_id = Column(UUID(as_uuid=True), unique=True, nullable=True)
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    full_name = Column(String(255), nullable=False)
    phone_number = Column(String(50), nullable=True)
    role = Column(String(50), default="restaurant_owner")
    avatar_url = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    restaurant = relationship("Restaurant", back_populates="users")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    whatsapp_number = Column(String(50), nullable=False)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    loyalty_points = Column(Integer, default=0)
    total_orders = Column(Integer, default=0)
    total_spent = Column(Numeric(12, 2), default=0.00)
    dietary_preference = Column(String(50), default="veg")
    is_blocked = Column(Boolean, default=False)
    last_order_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    restaurant = relationship("Restaurant", back_populates="customers")
    orders = relationship("Order", back_populates="customer")


class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    display_order = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)
    image_url = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    restaurant = relationship("Restaurant", back_populates="categories")
    items = relationship("MenuItem", back_populates="category", cascade="all, delete-orphan")


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    discount_price = Column(Numeric(10, 2), nullable=True)
    dietary_type = Column(String(50), default="veg")
    spice_level = Column(String(50), default="medium")
    preparation_time_minutes = Column(Integer, default=15)
    calories = Column(Integer, nullable=True)
    is_available = Column(Boolean, default=True)
    is_special = Column(Boolean, default=False)
    is_bestseller = Column(Boolean, default=False)
    image_url = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    restaurant = relationship("Restaurant", back_populates="menu_items")
    category = relationship("Category", back_populates="items")


class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    order_number = Column(String(50), unique=True, nullable=False)
    status = Column(String(50), default="pending")
    order_type = Column(String(50), default="delivery")
    delivery_address = Column(Text, nullable=True)
    subtotal = Column(Numeric(10, 2), nullable=False)
    tax_amount = Column(Numeric(10, 2), default=0.00)
    delivery_fee = Column(Numeric(10, 2), default=0.00)
    packing_charge = Column(Numeric(10, 2), default=0.00)
    discount_amount = Column(Numeric(10, 2), default=0.00)
    total_amount = Column(Numeric(10, 2), nullable=False)
    special_instructions = Column(Text, nullable=True)
    whatsapp_message_id = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    restaurant = relationship("Restaurant", back_populates="orders")
    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payment = relationship("Payment", back_populates="order", uselist=False)


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    menu_item_id = Column(UUID(as_uuid=True), ForeignKey("menu_items.id"), nullable=False)
    item_name = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    modifiers = Column(JSONB, default={})
    special_notes = Column(Text, nullable=True)

    order = relationship("Order", back_populates="items")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    gateway = Column(String(50), nullable=False)
    payment_link_id = Column(String(255), nullable=True)
    payment_link_url = Column(Text, nullable=True)
    transaction_reference = Column(String(255), nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), default="INR")
    status = Column(String(50), default="pending")
    paid_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    order = relationship("Order", back_populates="payment")
