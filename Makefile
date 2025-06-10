.PHONY: help dev stop clean build test deploy

help: ## 顯示幫助訊息
	@grep -E '^[a-zA-Z_-]+:.*?## .*$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $1, $2}'

dev: ## 啟動開發環境
	@echo "🚀 啟動 BeanThere 開發環境..."
	@docker-compose -f docker-compose.dev.yml up -d
	@echo "✅ 開發環境已啟動"
	@echo "📱 LINE Bot Webhook: http://localhost:5000/webhook"
	@echo "🌐 Web App: http://localhost:3000"
	@echo "🔧 API 文件: http://localhost:8000/docs"

stop: ## 停止開發環境
	@echo "⏹️ 停止開發環境..."
	@docker-compose -f docker-compose.dev.yml down
	@echo "✅ 開發環境已停止"

clean: ## 清理 Docker 資源
	@echo "🧹 清理 Docker 資源..."
	@docker-compose -f docker-compose.dev.yml down -v
	@docker system prune -f
	@echo "✅ 清理完成"

build: ## 建置所有服務
	@echo "🔨 建置所有服務..."
	@docker-compose -f docker-compose.dev.yml build --no-cache
	@echo "✅ 建置完成"

logs: ## 查看服務日誌
	@docker-compose -f docker-compose.dev.yml logs -f

status: ## 查看服務狀態
	@docker-compose -f docker-compose.dev.yml ps

db-migrate: ## 執行資料庫遷移
	@echo "🗄️ 執行資料庫遷移..."
	@docker-compose -f docker-compose.dev.yml exec api alembic upgrade head
	@echo "✅ 資料庫遷移完成"

db-reset: ## 重置資料庫
	@echo "⚠️ 重置資料庫..."
	@docker-compose -f docker-compose.dev.yml down -v
	@docker-compose -f docker-compose.dev.yml up -d postgres
	@sleep 5
	@docker-compose -f docker-compose.dev.yml up -d
	@echo "✅ 資料庫重置完成"

test: ## 執行測試
	@echo "🧪 執行測試..."
	@docker-compose -f docker-compose.dev.yml exec api python -m pytest tests/ -v
	@echo "✅ 測試完成"

shell-api: ## 進入 API 容器
	@docker-compose -f docker-compose.dev.yml exec api bash

shell-db: ## 進入資料庫容器
	@docker-compose -f docker-compose.dev.yml exec postgres psql -U beanthere -d beanthere_dev
