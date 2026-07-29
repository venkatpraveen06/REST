-- ==============================================================================
-- AuraDine AI - Seed Data for Multi-Tenant Testing
-- ==============================================================================

-- 1. Insert Demo Restaurant
INSERT INTO public.restaurants (id, name, slug, logo_url, phone_number, whatsapp_phone_number_id, currency, currency_symbol, is_active, is_verified)
VALUES (
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    'Aura Bistro & Grill',
    'aura-bistro',
    'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=300',
    '+919876543210',
    '1092837465',
    'INR',
    '₹',
    true,
    true
) ON CONFLICT (id) DO NOTHING;

-- 2. Insert Settings
INSERT INTO public.restaurant_settings (restaurant_id, auto_accept_orders, tax_percentage, packing_charge, delivery_fee_per_km, min_order_amount, opening_time, closing_time)
VALUES (
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    true,
    5.00,
    15.00,
    10.00,
    150.00,
    '10:00:00',
    '23:00:00'
) ON CONFLICT (restaurant_id) DO NOTHING;

-- 3. Insert Branch
INSERT INTO public.branches (id, restaurant_id, name, address, city, pincode, phone, is_main)
VALUES (
    'b1b2c3d4-e5f6-7890-abcd-ef1234567891',
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    'Indiranagar Main',
    '100 Feet Road, Indiranagar',
    'Bengaluru',
    '560038',
    '+919876543210',
    true
) ON CONFLICT (id) DO NOTHING;

-- 4. Insert Owner User
INSERT INTO public.users (id, restaurant_id, email, password_hash, full_name, phone_number, role)
VALUES (
    'u1b2c3d4-e5f6-7890-abcd-ef1234567892',
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    'admin@aurabistro.com',
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeg6Lruj3vjPGga31lW', -- hashed 'password123'
    'Chef Vikram Seth',
    '+919876543210',
    'restaurant_owner'
) ON CONFLICT (email) DO NOTHING;

-- 5. Insert Categories
INSERT INTO public.categories (id, restaurant_id, name, slug, description, display_order, is_available)
VALUES 
('c1010000-0000-0000-0000-000000000001', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'Starters & Appetizers', 'starters', 'Delicious starters to jumpstart your feast', 1, true),
('c1020000-0000-0000-0000-000000000002', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'Gourmet Burgers', 'burgers', 'Handcrafted artisanal burgers with fries', 2, true),
('c1030000-0000-0000-0000-000000000003', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'Woodfired Pizza', 'pizza', 'Authentic sourdough pizzas baked in clay oven', 3, true),
('c1040000-0000-0000-0000-000000000004', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'Beverages & Shakes', 'beverages', 'Refreshing mocktails, craft shakes & cold brews', 4, true),
('c1050000-0000-0000-0000-000000000005', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'Decadent Desserts', 'desserts', 'Sweet treats to end your meal on a high note', 5, true)
ON CONFLICT (id) DO NOTHING;

-- 6. Insert Menu Items
INSERT INTO public.menu_items (id, restaurant_id, category_id, name, slug, description, price, dietary_type, spice_level, preparation_time_minutes, is_special, is_bestseller, image_url)
VALUES
('m2010000-0000-0000-0000-000000000001', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'c1010000-0000-0000-0000-000000000001', 'Crispy Paneer Tikka Pops', 'paneer-tikka-pops', 'Cottage cheese cubes tossed in spicy tandoori marinade', 280.00, 'veg', 'spicy', 15, true, true, 'https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?w=500'),
('m2020000-0000-0000-0000-000000000002', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'c1010000-0000-0000-0000-000000000001', 'Fiery Chicken Wings (6pcs)', 'fiery-chicken-wings', 'Glazed wings with ghost pepper honey sauce', 340.00, 'non_veg', 'extra_spicy', 18, false, true, 'https://images.unsplash.com/photo-1527477396000-e27163b481c2?w=500'),
('m2030000-0000-0000-0000-000000000003', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'c1020000-0000-0000-0000-000000000002', 'Aura Smoky Truffle Cheeseburger', 'truffle-cheeseburger', 'Double smash chicken patty with black truffle aioli & cheddar', 420.00, 'non_veg', 'medium', 20, true, true, 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=500'),
('m2040000-0000-0000-0000-000000000004', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'c1020000-0000-0000-0000-000000000002', 'Garden Green Goddess Burger', 'veggie-burger', 'Crispy quinoa and bean patty with caramelized onion sauce', 320.00, 'veg', 'mild', 15, false, false, 'https://images.unsplash.com/photo-1550547660-d9450f859349?w=500'),
('m2050000-0000-0000-0000-000000000005', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'c1030000-0000-0000-0000-000000000003', 'Margherita Supreme Sourdough', 'margherita-pizza', 'San Marzano tomato, fresh mozzarella, fresh basil leaves', 390.00, 'veg', 'mild', 20, false, true, 'https://images.unsplash.com/photo-1604382354936-07c5d9983bd3?w=500'),
('m2060000-0000-0000-0000-000000000006', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'c1040000-0000-0000-0000-000000000004', 'Belgium Dark Chocolate Thickshake', 'chocolate-shake', 'Rich dark cocoa blended with cream and fudge brownie', 220.00, 'veg', 'mild', 10, false, true, 'https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=500')
ON CONFLICT (id) DO NOTHING;

-- 7. Insert Sample Customer
INSERT INTO public.customers (id, restaurant_id, whatsapp_number, name, loyalty_points, total_orders, total_spent, dietary_preference)
VALUES (
    'cust0000-0000-0000-0000-000000000001',
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    '+919988776655',
    'Aarav Sharma',
    150,
    3,
    1420.00,
    'non_veg'
) ON CONFLICT (id) DO NOTHING;

-- 8. Insert Sample Active Order for Kitchen Display
INSERT INTO public.orders (id, restaurant_id, branch_id, customer_id, order_number, status, order_type, delivery_address, subtotal, tax_amount, delivery_fee, packing_charge, total_amount, special_instructions)
VALUES (
    'ord00000-0000-0000-0000-000000000001',
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    'b1b2c3d4-e5f6-7890-abcd-ef1234567891',
    'cust0000-0000-0000-0000-000000000001',
    'ORD-20260729-0001',
    'preparing',
    'delivery',
    'Flat 402, Green Palms, 4th Cross Indiranagar, Bengaluru',
    760.00,
    38.00,
    30.00,
    15.00,
    843.00,
    'Less spicy, extra tissue papers please'
) ON CONFLICT (id) DO NOTHING;

INSERT INTO public.order_items (order_id, menu_item_id, item_name, quantity, unit_price, total_price, special_notes)
VALUES 
('ord00000-0000-0000-0000-000000000001', 'm2030000-0000-0000-0000-000000000003', 'Aura Smoky Truffle Cheeseburger', 1, 420.00, 420.00, 'Extra sauce'),
('ord00000-0000-0000-0000-000000000001', 'm2020000-0000-0000-0000-000000000002', 'Fiery Chicken Wings (6pcs)', 1, 340.00, 340.00, 'Medium spicy')
ON CONFLICT (id) DO NOTHING;
