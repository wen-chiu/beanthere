# Makefile
.PHONY: help setup start stop restart logs clean test

help:
	@echo "BeanThere 旅遊分帳系統"
	@echo ""
	@echo "可用指令："
	@echo "  setup    - 初始設定"
	@echo "  start    - 啟動服務"
	@echo "  stop     - 停止服務"
	@echo "  restart  - 重啟服務"
	@echo "  logs     - 查看日誌"
	@echo "  clean    - 清理資源"
	@echo "  test     - 執行測試"

setup:
	@chmod +x scripts/setup.sh
	@./scripts/setup.sh

start:
	@docker-compose up -d
	@echo "✅ 服務已啟動"

stop:
	@docker-compose down
	@echo "✅ 服務已停止"

restart:
	@docker-compose restart
	@echo "✅ 服務已重啟"

logs:
	@docker-compose logs -f

clean:
	@docker-compose down -v
	@docker system prune -f
	@echo "✅ 清理完成"

test:
	@echo "執行測試..."
	@docker-compose exec backend python -m pytest
	@echo "✅ 測試完成"


backend-logs:
	@docker-compose logs -f backend

linebot-logs:
	@docker-compose logs -f linebot

db-logs:
	@docker-compose logs -f postgres