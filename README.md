# 🚀 Stock Watcher

一个基于 AmericanBulls.com 的智能股票监控仪表盘，提供实时价格跟踪和交易信号分析。

## ✨ 核心功能

- 🎯 **自定义监控列表** - 添加/管理您关注的股票
- 📊 **实时价格监控** - 集成 Yahoo Finance 获取实时股价和涨跌幅  
- 🤖 **AI 信号抓取** - 自动抓取 AmericanBulls.com 的交易建议
- 📈 **可视化图表** - 分钟级价格图表和迷你曲线预览
- ⏰ **自动更新** - 后台定时任务每30分钟更新信号数据
- 📱 **响应式设计** - 支持桌面和移动设备访问

## 🏗️ 技术架构

### 后端
- **FastAPI** - 高性能 Python Web 框架
- **SQLAlchemy** - ORM 数据库管理
- **APScheduler** - 定时任务调度
- **BeautifulSoup** - 网页数据抓取
- **yfinance** - 股票价格数据

### 前端
- **HTML5 + CSS3 + JavaScript** - 纯前端实现
- **Chart.js** - 数据可视化
- **响应式布局** - 适配多种设备

### 部署
- **Docker** - 容器化部署
- **SQLite** - 轻量级数据库

## 🚀 快速开始

### 使用 Docker (推荐)

```bash
# 克隆项目
git clone https://github.com/your-username/stock-watcher.git
cd stock-watcher

# 启动服务
docker-compose up -d

# 访问应用
open http://localhost:3000
```

### 手动安装

#### 1. 后端设置
```bash
cd src/backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\\Scripts\\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 启动后端服务
uvicorn app:app --host 0.0.0.0 --port 8000
```

#### 2. 前端设置
```bash
cd src/frontend

# 启动前端服务
python -m http.server 3000
# 或使用 Node.js: npx serve -p 3000
```

#### 3. 访问应用
打开浏览器访问 `http://localhost:3000`

## 📋 使用指南

### 添加股票到监控列表
1. 在顶部输入框中输入股票代码（如 AAPL、MSFT）
2. 点击"添加"按钮
3. 股票将出现在监控表格中

### 查看详细信息
1. 点击表格中任意股票行
2. 弹出窗口显示详细的价格图表和交易信号
3. 包含 AmericanBulls 的最新建议和历史操作

### 删除股票
1. 在表格中找到要删除的股票
2. 点击删除按钮（如有）或通过 API 删除

## 🔧 配置选项

创建 `.env` 文件进行自定义配置：

```bash
# API 跨域设置
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# 数据库连接
DATABASE_URL=sqlite:///./stock_watch.db

# 更新频率（分钟）
SCHEDULER_INTERVAL_MINUTES=30

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/stock_watcher.log
```

## 📂 项目结构

```
stock-watcher/
├── src/
│   ├── backend/              # FastAPI 后端
│   │   ├── services/         # 业务逻辑服务
│   │   │   ├── americanbulls.py  # AB网站爬虫
│   │   │   └── prices.py     # 股价数据服务
│   │   ├── models.py         # 数据模型
│   │   ├── schemas.py        # API 数据模型
│   │   ├── app.py           # 主应用
│   │   └── requirements.txt  # Python 依赖
│   ├── frontend/            # Web 前端
│   │   ├── assets/          # CSS, JS 资源
│   │   │   ├── app.js       # 主 JavaScript
│   │   │   └── styles.css   # 样式文件
│   │   └── index.html       # 主页面
│   └── docker-compose.yml   # Docker 编排
├── docs/                    # 项目文档
│   ├── project-overview.md  # 项目概述
│   ├── api-documentation.md # API 文档
│   ├── web-scraping.md     # 爬虫文档
│   └── deployment.md       # 部署指南
├── logs/                   # 日志文件
├── README.md              # 本文件
└── .gitignore            # Git 忽略规则
```

## 🌐 API 端点

### 监控列表管理
- `GET /api/watchlist` - 获取监控列表
- `POST /api/watchlist` - 添加股票
- `DELETE /api/watchlist/{symbol}` - 删除股票

### 股票数据
- `GET /api/quote/{symbol}` - 获取实时报价
- `GET /api/chart/{symbol}` - 获取图表数据
- `GET /api/ab/{symbol}` - 获取 AmericanBulls 信号

详细 API 文档请查看 [docs/api-documentation.md](docs/api-documentation.md)

## 📊 数据源

- **股价数据**: Yahoo Finance API
- **交易信号**: AmericanBulls.com
- **图表数据**: yfinance 库

## ⚠️ 注意事项

- **数据延迟**: 股价数据可能有15-20分钟延迟
- **爬虫礼仪**: 遵循 AmericanBulls 网站的 robots.txt 和访问频率限制
- **仅供参考**: 所有数据和信号仅供参考，不构成投资建议

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🔗 相关链接

- [AmericanBulls.com](https://www.americanbulls.com/)
- [Yahoo Finance](https://finance.yahoo.com/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Chart.js 文档](https://www.chartjs.org/)

---

如有问题或建议，欢迎提交 Issue 或联系维护者。