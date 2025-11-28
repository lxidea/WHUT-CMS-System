from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "CMS-WHUT"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://cms_user:cms_password@localhost:5432/cms_whut"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000"]

    # Media
    MEDIA_DIR: str = "/app/media"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
