# 🍽️ AuraDine AI - Multi-Tenant AI Restaurant WhatsApp Ordering & Automation SaaS

AuraDine AI is an enterprise-grade, production-ready SaaS platform that turns WhatsApp into a restaurant's primary automated ordering, customer service, payment processing, and kitchen management engine.

---

## 🌟 Key Features

- 🤖 **Gemini 3.x Flash AI Intent Engine**: Natural language parsing for dish recommendations, dietary filters (*"Veg under ₹500"*, *"No onion"*, *"Spicy"*), and automatic cart assembly.
- 💬 **Meta WhatsApp Cloud API Integration**: Interactive button messages, quick replies, dynamic list menus, location sharing, and PDF invoice delivery.
- ⚡ **Multi-Tenant SaaS Architecture**: Strict row-level data isolation via Supabase PostgreSQL Row Level Security (RLS).
- 💳 **Seamless Payments**: Native Razorpay & Stripe payment link generation with automated instant webhook confirmation.
- 🍳 **Realtime Kitchen Display System (KDS)**: Dark mode kitchen ticket queue with preparation timers, audio alerts, and instant order state updates.
- 🔄 **n8n Automation Workflows**: Complete set of 15 automated JSON workflows for EOD sales reports, abandoned cart reminders, low stock alerts, and post-delivery review collection.

---

## 🚀 Quick Start Guide

### 1. Database Setup (Supabase)
Execute the migration scripts in your Supabase SQL Editor:
```bash
# 1. Apply Schema & RLS Policies
supabase/migrations/001_initial_schema.sql

# 2. Load Demo Seed Data
supabase/seed.sql
```

### 2. Launching via Docker Compose
```bash
cp .env.example .env
# Edit your API keys in .env

docker-compose -f docker/docker-compose.yml up -d --build
```

Access services at:
- **Frontend & Executive Dashboard**: `http://localhost`
- **Kitchen Display System (KDS)**: `http://localhost/kitchen.html`
- **FastAPI OpenAPI Swagger Docs**: `http://localhost:8000/docs`
- **n8n Automation Console**: `http://localhost:5678`

---

## 📁 Repository Architecture

```
/REST
├── backend/                  # FastAPI Python 3.12 API Engine
│   ├── app/
│   │   ├── api/v1/endpoints/ # Modular API Routes (Auth, Menu, Orders, WhatsApp, AI)
│   │   ├── core/             # Database & Security Config
│   │   ├── models/           # SQLAlchemy ORM Models
│   │   ├── schemas/          # Pydantic Request/Response Schemas
│   │   └── services/         # Gemini AI, Meta WhatsApp & Payment Wrappers
│   ├── Dockerfile
│   └── requirements.txt
├── supabase/
│   ├── migrations/           # Full PostgreSQL Schema with RLS Policies & Triggers
│   └── seed.sql              # Demo Restaurant & Menu Seed Data
├── n8n/
│   ├── workflows/            # Exportable n8n Automation Workflows (.json)
│   └── README.md
├── frontend/                 # Glassmorphism UI (Dashboard, KDS & Landing Page)
│   ├── css/styles.css
│   ├── js/
│   ├── dashboard.html
│   ├── kitchen.html
│   └── index.html
├── docker/
│   ├── docker-compose.yml
│   └── nginx.conf
├── docs/                     # Full Technical Documentation
└── .env.example
```
