import json
import logging
from typing import Dict, Any, List, Optional
from google import genai
from google.genai import types
from app.core.config import settings

logger = logging.getLogger("gemini_service")

class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.client = None
        if self.api_key and self.api_key != "your-gemini-api-key":
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini Client: {e}")

    async def parse_whatsapp_message(
        self,
        user_message: str,
        restaurant_name: str,
        menu_items_summary: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Parses natural language WhatsApp messages using Gemini 3.x Flash.
        Detects customer intent, dietary requirements, food items requested, quantity, and recommendations.
        """
        system_instruction = f"""
        You are AuraDine AI, an intelligent food ordering assistant for '{restaurant_name}'.
        Your goal is to parse customer WhatsApp messages, detect intent, recommend items, and assemble order carts.

        AVAILABLE MENU ITEMS:
        {json.dumps(menu_items_summary, indent=2)}

        OUTPUT FORMAT:
        Respond strictly with a JSON object matching this structure:
        {{
            "intent": "greeting | view_menu | place_order | recommend_food | track_order | payment | general_query",
            "reply_text": "Friendly, professional WhatsApp response text with emojis.",
            "detected_items": [
                {{
                    "item_id": "menu_item_id_uuid",
                    "item_name": "Exact Name",
                    "quantity": 1,
                    "unit_price": 280.0,
                    "special_notes": "no onion"
                }}
            ],
            "dietary_preference": "veg | non_veg | jain | null",
            "max_budget": float or null,
            "interactive_buttons": [
                {{"id": "btn_menu", "title": "📖 View Menu"}},
                {{"id": "btn_specials", "title": "⭐ Specials"}}
            ]
        }}
        """

        prompt = f"Customer Message: \"{user_message}\""

        # Fallback parsing if Gemini API key is default or unavailable
        if not self.client:
            return self._fallback_nlp_parser(user_message, menu_items_summary)

        try:
            response = self.client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.2,
                    response_mime_type="application/json"
                )
            )
            parsed_result = json.loads(response.text)
            return parsed_result
        except Exception as e:
            logger.error(f"Gemini API Error: {e}")
            return self._fallback_nlp_parser(user_message, menu_items_summary)

    def _fallback_nlp_parser(self, user_message: str, menu_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        msg_lower = user_message.lower()
        
        # Simple intent matching engine
        if any(w in msg_lower for w in ["hi", "hello", "hey", "start", "welcome"]):
            return {
                "intent": "greeting",
                "reply_text": "Welcome to Aura Bistro & Grill 🍽️\n\n⭐ 4.9 Rating | Open 10 AM - 11 PM\nHow may I assist you today?",
                "detected_items": [],
                "interactive_buttons": [
                    {"id": "btn_menu", "title": "📖 View Menu"},
                    {"id": "btn_specials", "title": "⭐ Today's Specials"},
                    {"id": "btn_order", "title": "🛒 Place Order"}
                ]
            }
        elif any(w in msg_lower for w in ["menu", "categories", "food list"]):
            return {
                "intent": "view_menu",
                "reply_text": "Here is our handcrafted menu! Select a category or ask for recommendations like 'Vegetarian under ₹500':",
                "detected_items": [],
                "interactive_buttons": [
                    {"id": "cat_starters", "title": "🍟 Starters"},
                    {"id": "cat_burgers", "title": "🍔 Burgers"},
                    {"id": "cat_pizza", "title": "🍕 Pizza"}
                ]
            }
        elif "burger" in msg_lower:
            matched_item = next((item for item in menu_items if "burger" in item["name"].lower()), None)
            items = []
            if matched_item:
                items.append({
                    "item_id": matched_item["id"],
                    "item_name": matched_item["name"],
                    "quantity": 1,
                    "unit_price": float(matched_item["price"]),
                    "special_notes": None
                })
            return {
                "intent": "place_order",
                "reply_text": f"Added {matched_item['name'] if matched_item else 'Burger'} to your cart! 🛒\nTotal: ₹{matched_item['price'] if matched_item else 420.00}\nWould you like to confirm your order?",
                "detected_items": items,
                "interactive_buttons": [
                    {"id": "confirm_checkout", "title": "✅ Pay & Confirm"},
                    {"id": "add_more", "title": "➕ Add Drinks"}
                ]
            }
        
        return {
            "intent": "general_query",
            "reply_text": "I can help you browse our menu, suggest dishes based on your dietary preferences, or place an order for delivery. Type 'Menu' or ask 'Suggest spicy food under ₹400'!",
            "detected_items": [],
            "interactive_buttons": [
                {"id": "btn_menu", "title": "📖 View Menu"}
            ]
        }

gemini_service = GeminiService()
