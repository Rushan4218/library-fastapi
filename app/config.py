import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    APP_NAME: str = "FastAPI Library Management API"
    APP_VERSION: str = "1.0.0"
    
    # Database Configuration
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/library_db"

    # Admin Auth Configuration
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "adminsecret"

    # Security Configuration
    SECRET_KEY: str = "e839174fb2461d31a55b1bf185c6b907c08e5e89d150244f71a933f7c46ef85d"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
