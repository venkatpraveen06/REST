# AuraDine AI - API Documentation

The AuraDine AI backend is built on **FastAPI** and offers complete OpenAPI / Swagger documentation out-of-the-box at `/docs`.

## Base URL
- Production: `https://api.auradine.com/api/v1`
- Local Development: `http://localhost:8000/api/v1`

---

## 🔑 Authentication Endpoints
### `POST /auth/register`
Registers a new restaurant tenant and owner account.
```json
{
  "email": "owner@restaurant.com",
  "password": "SecurePassword123!",
  "full_name": "Chef Gordon",
  "phone_number": "+919876543210",
  "restaurant_name": "Gourmet Bistro"
}
```

### `POST /auth/login`
Authenticates a restaurant staff/owner user and returns a multi-tenant JWT token containing `restaurant_id` and `role`.

---

## 💬 WhatsApp Automation Endpoints
### `GET /whatsapp/webhook`
Meta WhatsApp Cloud API Webhook Verification Endpoint (`hub.verify_token`).

### `POST /whatsapp/webhook`
Receives customer WhatsApp incoming webhooks, dispatches messages to Gemini AI Engine, generates interactive buttons, and returns automated responses.

---

## 🤖 Gemini AI Intent Parsing Endpoint
### `POST /ai/parse-intent`
Direct intent parser testing endpoint.
```json
{
  "restaurant_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "customer_whatsapp": "+919988776655",
  "user_message": "Suggest 2 spicy burgers under ₹500"
}
```

---

## 💳 Payment Link Generation Endpoint
### `POST /payments/generate-link`
Generates a dynamic Razorpay or Stripe payment link for a given order and pushes it directly to the customer's WhatsApp chat with a "Pay Now" interactive CTA button.
