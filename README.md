# BeanThere 旅遊分帳系統

基於 LINE Bot 和 Web App 的旅遊分帳日記系統 MVP 版本。

## 功能特色

- 🤖 **LINE Bot 介面**: 透過 LINE 輕鬆記帳和查看分帳結果
- 🌐 **Web App**: 完整的 LIFF 網頁應用程式
- 📊 **智能分帳**: 自動計算分帳結果和統計圖表
- 📱 **OCR 收據辨識**: AI 自動讀取收據資訊
- 🏷️ **消費分類**: 自動分類並生成預算報告
- 📝 **旅行日記**: 記錄美好的旅行回憶

## 快速開始

### 系統需求

- macOS 13.0+
- Docker Desktop 4.15+
- Node.js 18+
- Python 3.9+

### 安裝步驟

1. **執行安裝腳本**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

2. **設定環境變數**
   ```bash
   cp .env.example .env
   # 編輯 .env 檔案，設定 LINE Bot 和其他服務的 API Keys
   ```

3. **啟動開發環境**
   ```bash
   make dev
   ```

4. **訪問應用程式**
   - Web App: http://localhost:3000
   - API 文件: http://localhost:8000/docs
   - LINE Bot Webhook: http://localhost:5000/webhook

## 開發指令

```bash
make help          # 顯示所有可用指令
make dev           # 啟動開發環境
make stop          # 停止開發環境
make clean         # 清理 Docker 資源
make logs          # 查看服務日誌
make test          # 執行測試
make db-migrate    # 執行資料庫遷移
```

## 專案結構

```
beanthere/
├── frontend/           # 前端應用
│   ├── line-bot/      # LINE Bot
│   └── web-app/       # Vue.js Web App
├── backend/           # FastAPI 後端
├── services/          # 微服務
├── database/          # 資料庫設定
├── deployment/        # 部署配置
└── docs/             # 文件
```

## LINE Bot 設定

1. 前往 [LINE Developers Console](https://developers.line.biz/)
2. 建立新的 Messaging API Channel
3. 取得 Channel Secret 和 Channel Access Token
4. 設定 Webhook URL: `https://your-domain.com/webhook`
5. 更新 `.env` 檔案中的 LINE Bot 配置

## 貢獻指南

1. Fork 專案
2. 建立功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交變更 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)  
5. 開啟 Pull Request

## 授權條款

MIT License