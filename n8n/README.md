# AuraDine AI - n8n Automation Workflows Guide

This folder contains pre-configured production JSON workflows for **n8n Automation Engine**.

## Included Workflows:
1. `01_whatsapp_welcome_intent.json`: Receives WhatsApp webhook -> Invokes Gemini AI -> Sends interactive response.
2. `05_payment_success_kitchen_n8n.json`: Catches Razorpay payment webhook -> Updates DB -> Triggers Realtime Kitchen Display alert.

## How to Import in n8n:
1. Open your n8n Instance (e.g. `http://localhost:5678`).
2. Go to **Workflows** -> **Import from File**.
3. Select the target `.json` file.
4. Replace `YOUR_PHONE_ID` and `YOUR_WHATSAPP_TOKEN` credentials in the HTTP Request nodes.
5. Click **Activate Workflow**.
