# AuraDine AI - Production Deployment & Best Practices Guide

## Prerequisites
- Linux Server (Ubuntu 22.04 LTS or Debian 12)
- Docker & Docker Compose installed
- Domain with SSL certificate (Certbot / Let's Encrypt)
- Meta Developer Account (WhatsApp Cloud API App)
- Google Cloud Gemini API Key
- Supabase Cloud Account or Self-Hosted Supabase Instance

## Production Deployment Steps

1. **Clone Repository to Server**:
   ```bash
   git clone https://github.com/your-org/auradine-ai.git
   cd auradine-ai
   ```

2. **Configure Environment File**:
   ```bash
   cp .env.example .env
   nano .env
   ```
   *Fill in your production Supabase, Gemini, WhatsApp, and Razorpay API credentials.*

3. **Deploy Database Migrations**:
   Run `supabase/migrations/001_initial_schema.sql` in your Supabase SQL Editor.

4. **Launch Docker Services**:
   ```bash
   docker-compose -f docker/docker-compose.yml up -d --build
   ```

5. **Configure WhatsApp Cloud API Webhook URL**:
   In Meta Developer Console -> WhatsApp -> Configuration:
   - Webhook URL: `https://yourdomain.com/api/v1/whatsapp/webhook`
   - Verify Token: Matches `WHATSAPP_VERIFY_TOKEN` in `.env`.
   - Subscribe to fields: `messages`.

6. **Verify Monitoring & Logs**:
   ```bash
   docker-compose -f docker/docker-compose.yml logs -f backend
   ```
