#!/bin/bash
# setup.sh - BeanThere 系統快速設置腳本

set -e

echo "🚀 BeanThere 旅遊分帳系統安裝開始..."

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 檢查系統需求
check_requirements() {
    echo "🔍 檢查系統需求..."
    
    # 檢查 macOS 版本
    if [[ "$OSTYPE" != "darwin"* ]]; then
        echo -e "${RED}❌ 此腳本需要在 macOS 上執行${NC}"
        exit 1
    fi
    
    # 檢查 Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker 未安裝，請先安裝 Docker Desktop${NC}"
        echo "下載連結: https://www.docker.com/products/docker-desktop"
        exit 1
    fi
    
    # 檢查 Docker 是否運行
    if ! docker info > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Docker 未啟動，請啟動 Docker Desktop 後再執行此腳本${NC}"
        exit 1
    fi
    
    # 檢查 Node.js
    if ! command -v node &> /dev/null; then
        echo -e "${YELLOW}⚠️  Node.js 未安裝，正在安裝...${NC}"
        # 使用 Homebrew 安裝 Node.js
        if command -v brew &> /dev/null; then
            brew install node
        else
            echo -e "${RED}❌ 請先安裝 Homebrew 或手動安裝 Node.js 18+${NC}"
            exit 1
        fi
    fi
    
    # 檢查 Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 未安裝${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 系統需求檢查完成${NC}"
}

# 創建專案結構
create_project_structure() {
    echo "📁 創建專案結構..."
    
    # 創建主要目錄
    mkdir -p {frontend/{line-bot/{handlers,templates,utils},web-app/{src/{components,pages,services,store,router,utils},public}},backend/{app/{api/v1/endpoints,config,models,schemas,services,utils,tests}},services/{ocr-service/{processors,parsers,utils},ai-service/{models,utils},report-service/{generators,templates}},database/{migrations,seeds},deployment/{docker,k8s,scripts,nginx},docs,tests/{integration,e2e},scripts,uploads,credentials,ssl,logs}
    
    echo -e "${GREEN}✅ 專案結構創建完成${NC}"
}


# 創建環境變數範本
create_env_template() {
    # 複製為實際使用的 .env 檔案
    if [ ! -f .env ]; then
        cp .env.example .env
        echo -e "${YELLOW}⚠️  請編輯 .env 檔案，設定您的 LINE Bot 和其他服務的 API Keys${NC}"
    fi
    
    echo -e "${GREEN}✅ 環境變數範本創建完成${NC}"
}


# 創建 FastAPI 後端基礎檔案
create_backend_files() {
    echo "🔧 創建後端 API 基礎檔案..."
    
    # requirements.txt
    cat > backend/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
redis==5.0.1
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
aiofiles==23.2.1
httpx==0.25.2
pillow==10.1.0
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
EOF

    # Dockerfile.dev
    cat > backend/Dockerfile.dev << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 安裝 Python 依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
EOF

    # main.py
    cat > backend/app/main.py << 'EOF'
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.api.v1.api import api_router
from app.config.settings import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="BeanThere 旅遊分帳系統 API",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 開發環境允許所有來源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 靜態檔案服務
if not os.path.exists("uploads"):
    os.makedirs("uploads")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# API 路由
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "BeanThere API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
EOF

    # settings.py
    cat > backend/app/config/settings.py << 'EOF'
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "BeanThere"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    
    # 資料庫設定
    DATABASE_URL: str = "postgresql://beanthere:dev_password@localhost:5432/beanthere_dev"
    
    # Redis 設定
    REDIS_URL: str = "redis://localhost:6379"
    
    # JWT 設定
    SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # LINE Bot 設定
    LINE_CHANNEL_SECRET: Optional[str] = None
    LINE_CHANNEL_ACCESS_TOKEN: Optional[str] = None
    
    # 檔案上傳設定
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_FOLDER: str = "uploads"
    
    class Config:
        env_file = ".env"

settings = Settings()
EOF

    echo -e "${GREEN}✅ 後端基礎檔案創建完成${NC}"
}

# 創建 LINE Bot 基礎檔案
create_linebot_files() {
    echo "🤖 創建 LINE Bot 基礎檔案..."
    
    # requirements.txt
    cat > frontend/line-bot/requirements.txt << 'EOF'
flask==3.0.0
line-bot-sdk==3.5.0
requests==2.31.0
python-dotenv==1.0.0
gunicorn==21.2.0
EOF

    # Dockerfile.dev
    cat > frontend/line-bot/Dockerfile.dev << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
EOF

    # app.py
    cat > frontend/line-bot/app.py << 'EOF'
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__)

# LINE Bot 設定
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

# API 基礎 URL
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')

@app.route("/webhook", methods=['POST'])
def webhook():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    
    # 簡單的指令處理
    if user_message == "開始記帳":
        reply_text = "歡迎使用 BeanThere！請選擇功能：\n1. 新增旅行\n2. 記錄支出\n3. 查看分帳結果"
    elif "新增旅行" in user_message:
        reply_text = "請輸入旅行名稱和日期，格式：\n旅行名稱｜開始日期｜結束日期\n例：東京之旅｜2024-03-15｜2024-03-20"
    else:
        reply_text = f"收到訊息：{user_message}\n輸入「開始記帳」來使用功能"
    
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

@app.route("/")
def index():
    return "BeanThere LINE Bot is running!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
EOF

    echo -e "${GREEN}✅ LINE Bot 基礎檔案創建完成${NC}"
}

# 創建 Vue.js Web App 基礎檔案
create_webapp_files() {
    echo "🌐 創建 Web App 基礎檔案..."
    
    # package.json
    cat > frontend/web-app/package.json << 'EOF'
{
  "name": "beanthere-webapp",
  "version": "1.0.0",
  "description": "BeanThere 旅遊分帳系統 Web App",
  "scripts": {
    "serve": "vue-cli-service serve",
    "build": "vue-cli-service build",
    "lint": "vue-cli-service lint"
  },
  "dependencies": {
    "@line/liff": "^2.22.3",
    "vue": "^3.3.8",
    "vue-router": "^4.2.5",
    "vuex": "^4.1.0",
    "axios": "^1.6.2",
    "chart.js": "^4.4.0",
    "vue-chartjs": "^5.2.0",
    "element-plus": "^2.4.4",
    "@element-plus/icons-vue": "^2.1.0"
  },
  "devDependencies": {
    "@vue/cli-service": "^5.0.8",
    "vue-template-compiler": "^2.7.15"
  }
}
EOF

    # Dockerfile.dev
    cat > frontend/web-app/Dockerfile.dev << 'EOF'
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "serve"]
EOF

    # Vue 主檔案
    cat > frontend/web-app/src/main.js << 'EOF'
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

const app = createApp(App)

app.use(store)
app.use(router)
app.use(ElementPlus)

app.mount('#app')
EOF

    echo -e "${GREEN}✅ Web App 基礎檔案創建完成${NC}"
}

# 創建 Nginx 配置
create_nginx_config() {
    echo "🌐 創建 Nginx 配置..."
    
    cat > deployment/nginx/dev.conf << 'EOF'
server {
    listen 80;
    server_name localhost;
    
    # Web App
    location / {
        proxy_pass http://webapp:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # API
    location /api/ {
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # LINE Bot Webhook
    location /webhook {
        proxy_pass http://linebot:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

    echo -e "${GREEN}✅ Nginx 配置創建完成${NC}"
}

# 完成安裝後的訊息
show_completion_message() {
    echo ""
    echo "🎉 BeanThere 系統安裝完成！"
    echo ""
    echo -e "${GREEN}下一步操作：${NC}"
    echo "1. 編輯 .env 檔案，設定您的 LINE Bot API Keys"
    echo "2. 執行 'make dev' 啟動開發環境"
    echo "3. 訪問 http://localhost:8000/docs 查看 API 文件"
    echo ""
    echo -e "${YELLOW}重要提醒：${NC}"
    echo "- 請確保 Docker Desktop 已啟動"
    echo "- LINE Bot 需要 HTTPS 網址，建議使用 ngrok 進行測試"
    echo "- 詳細說明請參考 README.md"
    echo ""
    echo -e "${GREEN}祝您開發愉快！ 🚀${NC}"
}

# 主要執行流程
main() {
    check_requirements
    # create_project_structure
    create_env_template
    # create_backend_files
    # create_linebot_files
    # create_webapp_files
    # create_nginx_config
    show_completion_message
}

# 執行主函數
main "$@"