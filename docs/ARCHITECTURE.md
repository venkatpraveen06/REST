# AuraDine AI - System Architecture Document

## High Level Overview

```
 Customer (WhatsApp)
        │
        ▼
 Meta WhatsApp Cloud API
        │
        ▼
 n8n Webhook / FastAPI Webhook
        │
        ├──► Gemini 3.x Flash AI (Intent & Recommendation Parser)
        │
        ▼
 FastAPI Backend (Python 3.12 + SQLAlchemy)
        │
        ▼
 Supabase PostgreSQL (Multi-Tenant Row Level Security)
        │
   ┌────┴────────────────────────┐
   ▼                             ▼
 Executive Dashboard         Kitchen Display (KDS)
 (Realtime Updates)          (Audio & Visual Alerts)
```

## Security & Multi-Tenancy Architecture
1. **Tenant Isolation**: Every database table includes a `restaurant_id` foreign key.
2. **Supabase RLS Policies**: Row Level Security policies enforce read/write access based on authenticated JWT claims (`auth.uid()`).
3. **Data Encryption**: Sensitive API keys (Razorpay Key Secret, WhatsApp Access Token) are encrypted using AES-256 before storage.
