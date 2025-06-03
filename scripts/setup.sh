#!/bin/bash

echo "🚀 設定 BeanThere 旅遊分帳系統..."

# 檢查 Docker 是否安裝
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 尚未安裝，請先安裝 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 尚未安裝，請先安裝 Docker Compose"
    exit 1
fi

# 複製環境變數檔案
if [ ! -f .env ]; then
    echo "📝 建立環境變數檔案..."
    cp .env.example .env
    echo "⚠️  請編輯 .env 檔案，填入您的 LINE Bot 相關設定"
fi

# 建立必要的目錄
echo "📁 建立必要目錄..."
mkdir -p logs
mkdir -p uploads
mkdir -p frontend/web-app/dist

# 複製 LIFF 網頁到 dist 目錄
echo "📱 準備 LIFF 網頁檔案..."
cp liff_webapp.html frontend/web-app/dist/index.html

# 建立和啟動容器
echo "🐳 啟動 Docker 容器..."
docker-compose up -d --build

# 等待資料庫啟動
echo "⏳ 等待資料庫啟動..."
sleep 10

# 檢查服務狀態
echo "🔍 檢查服務狀態..."
docker-compose ps

echo ""
echo "✅ 設定完成！"
echo ""
echo "服務網址："
echo "- 後端 API: http://localhost:8000"
echo "- LINE Bot Webhook: http://localhost:5000/webhook"
echo "- LIFF 網頁: http://localhost"
echo ""
echo "請確認："
echo "1. 編輯 .env 檔案中的 LINE Bot 設定"
echo "2. 在 LINE Developers Console 設定 Webhook URL"
echo "3. 設定 LIFF 應用程式"
echo ""
echo "查看日誌: docker-compose logs -f [服務名稱]"
echo "停止服務: docker-compose down"