# app/config/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from urllib.parse import quote_plus

# 資料庫配置
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/beanthere_db"
)

# 處理特殊字符的密碼


def get_database_url():
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "password")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "beanthere_db")

    # URL 編碼密碼以處理特殊字符
    encoded_password = quote_plus(db_password)

    return f"postgresql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}"


# 創建資料庫引擎
engine = create_engine(
    get_database_url(),
    pool_pre_ping=True,
    pool_recycle=300,
    echo=os.getenv("DEBUG", "False").lower() == "true"
)

# 創建會話工廠
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 創建 Base 類
Base = declarative_base()

# 依賴注入：獲取資料庫會話


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()