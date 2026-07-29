from typing import List, Optional, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "AuraDine AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    
    # Security & CORS
    SECRET_KEY: str = "super_secret_jwt_key_auradine_ai_2026_production_change_this"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    ALLOWED_ORIGINS: Union[List[str], str] = ["*"]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    
    # Supabase Configuration
    SUPABASE_URL: str = "https://your-supabase-project.supabase.co"
    SUPABASE_ANON_KEY: str = "your-supabase-anon-key"
    SUPABASE_SERVICE_ROLE_KEY: str = "your-supabase-service-role-key"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
    
    # Google Gemini AI Configuration (Gemini 3.x Flash)
    GEMINI_API_KEY: str = "your-gemini-api-key"
    GEMINI_MODEL: str = "gemini-2.5-flash"
    
    # Meta WhatsApp Cloud API
    WHATSAPP_TOKEN: str = "your-whatsapp-access-token"
    WHATSAPP_PHONE_NUMBER_ID: str = "your-phone-number-id"
    WHATSAPP_VERIFY_TOKEN: str = "auradine_webhook_verify_secret_123"
    
    # Payment Gateways
    RAZORPAY_KEY_ID: str = "rzp_test_key"
    RAZORPAY_KEY_SECRET: str = "rzp_test_secret"
    STRIPE_SECRET_KEY: str = "sk_test_123"
    STRIPE_WEBHOOK_SECRET: str = "whsec_123"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
