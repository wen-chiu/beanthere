# app/config/settings.py
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 基本配置
    APP_NAME: str = "BeanThere"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # 資料庫設定
    DATABASE_URL: str = "postgresql://beanthere:dev_password@localhost:5432/beanthere_dev"

    # Redis 設定
    REDIS_URL: str = "redis://localhost:6379"

    # # LINE Bot 配置
    # LINE_CHANNEL_SECRET: Optional[str] = os.getenv("LINE_CHANNEL_SECRET")
    # LINE_CHANNEL_ACCESS_TOKEN: Optional[str] = os.getenv(
    #     "LINE_CHANNEL_ACCESS_TOKEN")
    # LINE Bot 設定
    LINE_CHANNEL_SECRET: Optional[str] = None
    LINE_CHANNEL_ACCESS_TOKEN: Optional[str] = None

    # # OCR 服務配置
    # OCR_SERVICE_URL: str = os.getenv(
    #     "OCR_SERVICE_URL", "http://localhost:8001")
    # GOOGLE_VISION_API_KEY: Optional[str] = os.getenv("GOOGLE_VISION_API_KEY")

    # AI 服務配置
    AI_SERVICE_URL: str = os.getenv("AI_SERVICE_URL", "http://localhost:8002")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")

    # JWT 設定
    SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # 檔案上傳配置
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_FOLDER: str = "uploads"

    # CORS 配置
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8080",
        "https://yourdomain.com"
    ]

    class Config:
        env_file = ".env"


settings = Settings()
