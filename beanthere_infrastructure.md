# BeanThere 旅遊分帳系統 - 完整基礎架構設計

## 一、系統架構概覽

### 架構圖
```
┌─────────────────────────────────────────────────────────────┐
│                        User Layer                           │
├─────────────────────────────────────────────────────────────┤
│  LINE Bot Client    │    LIFF Web App (Vue.js)              │
│  (Flex Messages)    │    (Progressive Web App)              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway / Load Balancer              │
│                        (Nginx)                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────-┐
│                   Application Layer                          │
├───────────────────────────────────────────────────────────-──┤
│  LINE Bot Service   │  Main API Service   │  Micro Services  │
│  (Python Flask)     │  (FastAPI)          │  (Docker)        │
│                     │                     │                  │
│  • Webhook Handler  │  • Trip Management  │  • OCR Service   │
│  • Message Router   │  • Member Management│  • AI Service    │
│  • Template Engine  │  • Expense Service  │  • Report Service│
└─────────────────────────────────────────────────────────────-┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────-──┐
│                         Data Layer                           │
├────────────────────────────────────────────────────────────-─┤
│  PostgreSQL        │  Redis Cache     │  File Storage        │
│  (Main Datadase)   │  (Session/Cache) │  (Images/Documents)  │
│                    │                  │                      │
│  • Users           │  • User Sessions │  • Receipt Images    │
│  • Trips           │  • API Cache     │  • Profile Photos    │
│  • Expenses        │  • Rate Limiting │  • Export Files      │
│  • Settlements     │                  │                      │
└────────────────────────────────────────────────────────────-─┘
```

## 二、本機開發環境設定

### 開發環境需求
- **macOS**: 13.0+ (Monterey 或更新版本)
- **Docker Desktop**: 4.15+
- **Python**: 3.9+
- **Node.js**: 18+
- **Git**: 2.30+

### 本機環境架構
```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  # 資料庫服務
  postgres:
    image: postgres:15
    container_name: beanthere_postgres
    environment:
      POSTGRES_DB: beanthere_dev
      POSTGRES_USER: beanthere
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql

  # Redis 快取服務
  redis:
    image: redis:7-alpine
    container_name: beanthere_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # 主要 API 服務
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    container_name: beanthere_api
    environment:
      - DATABASE_URL=postgresql://beanthere:dev_password@postgres:5432/beanthere_dev
      - REDIS_URL=redis://redis:6379
      - LINE_CHANNEL_SECRET=${LINE_CHANNEL_SECRET}
      - LINE_CHANNEL_ACCESS_TOKEN=${LINE_CHANNEL_ACCESS_TOKEN}
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - ./uploads:/app/uploads
    depends_on:
      - postgres
      - redis
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  # LINE Bot 服務
  linebot:
    build:
      context: ./frontend/line-bot
      dockerfile: Dockerfile.dev
    container_name: beanthere_linebot
    environment:
      - API_BASE_URL=http://api:8000
      - LINE_CHANNEL_SECRET=${LINE_CHANNEL_SECRET}
      - LINE_CHANNEL_ACCESS_TOKEN=${LINE_CHANNEL_ACCESS_TOKEN}
    ports:
      - "5000:5000"
    volumes:
      - ./frontend/line-bot:/app
    depends_on:
      - api
    command: python app.py

  # OCR 服務
  ocr-service:
    build:
      context: ./services/ocr-service
      dockerfile: Dockerfile.dev
    container_name: beanthere_ocr
    environment:
      - GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/gcp-key.json
    ports:
      - "8001:8000"
    volumes:
      - ./services/ocr-service:/app
      - ./credentials:/app/credentials
    command: uvicorn app:app --host 0.0.0.0 --port 8000 --reload

  # Web App (開發伺服器)
  webapp:
    build:
      context: ./frontend/web-app
      dockerfile: Dockerfile.dev
    container_name: beanthere_webapp
    environment:
      - VUE_APP_API_BASE_URL=http://localhost:8000
      - VUE_APP_LIFF_ID=${LIFF_ID}
    ports:
      - "3000:3000"
    volumes:
      - ./frontend/web-app:/app
      - /app/node_modules
    command: npm run serve

  # Nginx (本機反向代理)
  nginx:
    image: nginx:alpine
    container_name: beanthere_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./deployment/nginx/dev.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
      - linebot
      - webapp

volumes:
  postgres_data:
  redis_data:
```

### 本機開發啟動腳本
```bash
#!/bin/bash
# scripts/dev-setup.sh

echo "🚀 BeanThere 開發環境啟動中..."

# 檢查 Docker 是否運行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未啟動，請先啟動 Docker Desktop"
    exit 1
fi

# 建立必要目錄
mkdir -p uploads credentials ssl logs

# 複製環境變數範本
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  請設定 .env 檔案中的環境變數"
fi

# 啟動開發環境
docker-compose -f docker-compose.dev.yml up -d

echo "⏳ 等待服務啟動..."
sleep 10

# 檢查服務狀態
echo "🔍 檢查服務狀態..."
docker-compose -f docker-compose.dev.yml ps

# 執行資料庫遷移
echo "🗄️ 執行資料庫遷移..."
docker-compose -f docker-compose.dev.yml exec api python -m alembic upgrade head

echo "✅ 開發環境啟動完成!"
echo "📱 LINE Bot Webhook: http://localhost:5000/webhook"
echo "🌐 Web App: http://localhost:3000"
echo "🔧 API 文件: http://localhost:8000/docs"
```

## 三、雲端部署架構

### AWS 雲端架構
```
┌─────────────────────────────────────────────────────────────┐
│                        AWS Cloud                            │
├─────────────────────────────────────────────────────────────┤
│  Route 53 (DNS) → CloudFront (CDN) → ALB (Load Balancer)    │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      ECS Cluster                            │
├─────────────────────────────────────────────────────────────┤
│  ECS Service (Auto Scaling)                                 │
│  ├── API Service (FastAPI)                                  │
│  ├── LINE Bot Service (Flask)                               │
│  ├── OCR Service (Python)                                   │
│  └── Web App (Nginx + Vue.js)                               │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      Data Service                           │
├─────────────────────────────────────────────────────────────┤
│  RDS PostgreSQL  │  ElastiCache Redis  │  S3 Bucket         │
│  (Multi-AZ)      │  (Cluster Mode)     │  (File Storage)    │
└─────────────────────────────────────────────────────────────┘
```

### 部署配置檔案
```yaml
# deployment/docker-compose.prod.yml
version: '3.8'

services:
  api:
    image: beanthere/api:${VERSION}
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - LINE_CHANNEL_SECRET=${LINE_CHANNEL_SECRET}
      - LINE_CHANNEL_ACCESS_TOKEN=${LINE_CHANNEL_ACCESS_TOKEN}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - S3_BUCKET=${S3_BUCKET}
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  linebot:
    image: beanthere/linebot:${VERSION}
    environment:
      - API_BASE_URL=${API_BASE_URL}
      - LINE_CHANNEL_SECRET=${LINE_CHANNEL_SECRET}
      - LINE_CHANNEL_ACCESS_TOKEN=${LINE_CHANNEL_ACCESS_TOKEN}
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 256M
        reservations:
          memory: 128M

  webapp:
    image: beanthere/webapp:${VERSION}
    environment:
      - VUE_APP_API_BASE_URL=${API_BASE_URL}
      - VUE_APP_LIFF_ID=${LIFF_ID}
    deploy:
      replicas: 2

  nginx:
    image: beanthere/nginx:${VERSION}
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - api
      - linebot
      - webapp
```

### Terraform 基礎設施程式碼
```hcl
# deployment/terraform/main.tf
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC 設定
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "beanthere-vpc"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "beanthere-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# RDS PostgreSQL
resource "aws_db_instance" "main" {
  identifier = "beanthere-db"
  
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = "db.t3.micro"
  
  allocated_storage     = 20
  max_allocated_storage = 100
  storage_encrypted     = true
  
  db_name  = "beanthere"
  username = var.db_username
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = true
  deletion_protection = false
  
  tags = {
    Name = "beanthere-database"
  }
}

# ElastiCache Redis
resource "aws_elasticache_subnet_group" "main" {
  name       = "beanthere-cache-subnet"
  subnet_ids = aws_subnet.private[*].id
}

resource "aws_elasticache_cluster" "main" {
  cluster_id           = "beanthere-cache"
  engine               = "redis"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.main.name
  security_group_ids   = [aws_security_group.redis.id]
}

# S3 Bucket
resource "aws_s3_bucket" "uploads" {
  bucket = "beanthere-uploads-${random_string.bucket_suffix.result}"
}

resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}
```

## 四、監控與日誌

### 監控架構
```yaml
# monitoring/docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana/datasources:/etc/grafana/provisioning/datasources

  loki:
    image: grafana/loki:latest
    container_name: loki
    ports:
      - "3100:3100"
    volumes:
      - ./loki-config.yml:/etc/loki/local-config.yaml
      - loki_data:/loki

  promtail:
    image: grafana/promtail:latest
    container_name: promtail
    volumes:
      - /var/log:/var/log:ro
      - ./promtail-config.yml:/etc/promtail/config.yml

volumes:
  prometheus_data:
  grafana_data:
  loki_data:
```

## 五、CI/CD Pipeline

### GitHub Actions 工作流程
```yaml
# .github/workflows/deploy.yml
name: Deploy BeanThere

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
          
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install pytest pytest-cov
          
      - name: Run tests
        run: |
          cd backend
          pytest tests/ --cov=app --cov-report=xml
          
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ap-northeast-1
          
      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1
        
      - name: Build and push Docker images
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: beanthere
          IMAGE_TAG: ${{ github.sha }}
        run: |
          # Build API
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY-api:$IMAGE_TAG ./backend
          docker push $ECR_REGISTRY/$ECR_REPOSITORY-api:$IMAGE_TAG
          
          # Build LINE Bot
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY-linebot:$IMAGE_TAG ./frontend/line-bot
          docker push $ECR_REGISTRY/$ECR_REPOSITORY-linebot:$IMAGE_TAG
          
          # Build Web App
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY-webapp:$IMAGE_TAG ./frontend/web-app
          docker push $ECR_REGISTRY/$ECR_REPOSITORY-webapp:$IMAGE_TAG

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    
    steps:
      - name: Deploy to ECS
        run: |
          aws ecs update-service --cluster beanthere-cluster --service beanthere-api --force-new-deployment
          aws ecs update-service --cluster beanthere-cluster --service beanthere-linebot --force-new-deployment
          aws ecs update-service --cluster beanthere-cluster --service beanthere-webapp --force-new-deployment
```

## 六、安全性配置

### 安全性檢查清單
- [ ] **SSL/TLS 憑證**: Let's Encrypt 或 AWS Certificate Manager
- [ ] **API 認證**: JWT Token 驗證
- [ ] **資料庫加密**: 連線與儲存加密
- [ ] **環境變數**: AWS Parameter Store 或 Secrets Manager
- [ ] **網路安全**: VPC, Security Groups, NACL
- [ ] **檔案上傳**: 類型限制、大小限制、病毒掃描
- [ ] **API 限流**: Redis + sliding window
- [ ] **日誌記錄**: 不記錄敏感資訊
- [ ] **GDPR 合規**: 資料保護與刪除機制

### 環境變數管理
```bash
# .env.example
# 應用程式設定
APP_NAME=BeanThere
APP_ENV=development
DEBUG=true

# 資料庫設定
DATABASE_URL=postgresql://beanthere:password@localhost:5432/beanthere_dev
REDIS_URL=redis://localhost:6379

# LINE Bot 設定
LINE_CHANNEL_SECRET=your_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_access_token
LIFF_ID=your_liff_id

# 第三方服務
GOOGLE_APPLICATION_CREDENTIALS=path/to/gcp-key.json
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
S3_BUCKET=beanthere-uploads

# 安全性設定
JWT_SECRET=your_jwt_secret
ENCRYPTION_KEY=your_encryption_key
```

## 七、成本估算

### AWS 月費用估算 (MVP 階段)
- **ECS Fargate**: $30-50/月 (2 vCPU, 4GB RAM)
- **RDS PostgreSQL**: $15-25/月 (db.t3.micro)
- **ElastiCache Redis**: $10-15/月 (cache.t3.micro)
- **S3 + CloudFront**: $5-10/月
- **ALB**: $20/月
- **Route 53**: $0.5/月
- **總計**: 約 $80-120/月

### 本機開發成本
- **macOS 開發機**: 現有設備
- **Docker Desktop**: 免費
- **開發工具**: 免費 (VS Code, Git 等)
- **LINE Bot 開發**: 免費額度
- **總計**: $0/月

這個架構設計提供了完整的本機開發到雲端部署的解決方案，具有良好的可擴展性和維護性。