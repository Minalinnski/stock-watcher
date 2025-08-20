# Deployment Guide

## 环境要求

### 系统要求
- **Python**: 3.9+
- **Node.js**: 16+ (可选，用于前端开发)
- **Docker**: 20.10+ (推荐)
- **Docker Compose**: 2.0+

### 硬件要求
- **内存**: 最少 512MB，推荐 1GB+
- **存储**: 最少 1GB 可用空间
- **网络**: 稳定的互联网连接

## 部署方式

### 1. Docker 部署 (推荐)

#### 快速启动
```bash
# 克隆项目
git clone <repository-url>
cd stock-watcher

# 启动服务
docker-compose up -d
```

#### 配置文件
创建 `.env` 文件：
```bash
# API 配置
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# 数据库配置
DATABASE_URL=sqlite:///./stock_watch.db

# 调度器配置
SCHEDULER_INTERVAL_MINUTES=30

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/stock_watcher.log
```

#### Docker Compose 服务
```yaml
version: '3.8'
services:
  backend:
    build: ./src/backend
    ports:
      - "8000:8000"
    volumes:
      - ./logs:/app/logs
      - ./stock_watch.db:/app/stock_watch.db
    environment:
      - DATABASE_URL=sqlite:///./stock_watch.db
    
  frontend:
    build: ./src/frontend  
    ports:
      - "3000:80"
    depends_on:
      - backend
```

### 2. 手动部署

#### 后端部署
```bash
cd src/backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app:app --host 0.0.0.0 --port 8000
```

#### 前端部署
```bash
cd src/frontend

# 使用 Python 简单服务器
python -m http.server 3000

# 或使用 Node.js serve
npx serve -p 3000
```

### 3. 生产环境部署

#### Nginx 反向代理
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 前端静态文件
    location / {
        root /path/to/frontend;
        try_files $uri $uri/ /index.html;
    }
    
    # API 代理
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### Systemd 服务
创建 `/etc/systemd/system/stock-watcher.service`:
```ini
[Unit]
Description=Stock Watcher API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/stock-watcher/src/backend
Environment=PATH=/path/to/venv/bin
ExecStart=/path/to/venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl enable stock-watcher
sudo systemctl start stock-watcher
```

## 环境变量配置

### 必需配置
```bash
# 数据库
DATABASE_URL=sqlite:///./stock_watch.db

# 跨域设置
CORS_ORIGINS=http://localhost:3000
```

### 可选配置
```bash
# 调度器设置
SCHEDULER_INTERVAL_MINUTES=30

# 日志设置
LOG_LEVEL=INFO
LOG_FILE=logs/stock_watcher.log

# API 限制
MAX_WATCHLIST_SIZE=100
REQUEST_TIMEOUT=15

# 缓存设置
CACHE_TTL_MINUTES=30
```

## 数据库管理

### 初始化
数据库会在首次启动时自动创建表结构。

### 备份
```bash
# SQLite 备份
sqlite3 stock_watch.db ".backup backup_$(date +%Y%m%d).db"
```

### 迁移
如果需要更新数据库结构：
```bash
# 停止服务
docker-compose down

# 备份数据
cp stock_watch.db stock_watch.db.backup

# 重启服务（自动应用新结构）
docker-compose up -d
```

## 监控和维护

### 健康检查
```bash
# API 健康检查
curl http://localhost:8000/api/watchlist

# 服务状态检查
docker-compose ps
```

### 日志查看
```bash
# Docker 日志
docker-compose logs -f backend

# 文件日志
tail -f logs/stock_watcher.log
```

### 性能监控
- CPU 使用率
- 内存占用
- 数据库大小
- API 响应时间

### 定期维护
```bash
# 清理旧日志
find logs/ -name "*.log" -mtime +30 -delete

# 数据库优化
sqlite3 stock_watch.db "VACUUM;"

# Docker 镜像清理
docker system prune -f
```

## 故障排除

### 常见问题

#### 1. 端口占用
```bash
# 检查端口使用
lsof -i :8000
netstat -tulpn | grep :8000

# 修改端口
export PORT=8001
```

#### 2. 权限问题
```bash
# 确保日志目录权限
chmod 755 logs/
chmod 666 logs/*.log
```

#### 3. 网络连接问题
```bash
# 测试外部 API 连接
curl -I "https://www.americanbulls.com"
curl -I "https://finance.yahoo.com"
```

#### 4. 数据库锁定
```bash
# SQLite 数据库解锁
fuser -v stock_watch.db
kill -9 <process_id>
```

### 性能优化

#### 1. 并发处理
```python
# uvicorn 启动参数
uvicorn app:app --workers 4 --host 0.0.0.0 --port 8000
```

#### 2. 缓存优化
- 增加缓存有效期
- 使用 Redis 替代内存缓存
- 实现数据预加载

#### 3. 数据库优化
- 定期 VACUUM 操作
- 添加适当索引
- 考虑迁移到 PostgreSQL