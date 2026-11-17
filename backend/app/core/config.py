from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from decimal import Decimal
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Food Manufacturing Order-to-Audit ERP"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "food-erp-super-secret-jwt-key-2026-audit-nit-trichy"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # Database Configuration
    DATABASE_URL: str = "sqlite:///./food_erp.db"

    # Company GST Details (South Indian Food Manufacturer in Tamil Nadu)
    COMPANY_NAME: str = "Sri Ranganatha Traditional Foods LLP"
    COMPANY_GSTIN: str = "33AABCS9876Q1Z2"
    COMPANY_STATE: str = "Tamil Nadu"
    COMPANY_STATE_CODE: str = "33"
    COMPANY_ADDRESS: str = "B-14 SIDCO Industrial Estate, Thuvakudi, Tiruchirappalli, Tamil Nadu - 620015"
    COMPANY_PHONE: str = "+91 431 2503000"
    COMPANY_EMAIL: str = "contact@ranganathafoods.in"

    # Business Logic Rules
    VARIANCE_ALERT_THRESHOLD_PERCENT: float = 3.0

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def sync_database_url(self) -> str:
        # Standardize PostgreSQL URL dialect for SQLAlchemy
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url

settings = Settings()

