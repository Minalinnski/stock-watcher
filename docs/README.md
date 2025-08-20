# 📚 Documentation Index

欢迎查看 Stock Watcher 项目文档！

## 📋 文档目录

### 🎯 [项目概述](project-overview.md)
- 项目功能介绍
- 技术架构说明
- 数据流程图解
- 使用场景分析

### 🔌 [API 文档](api-documentation.md)
- 完整的 REST API 端点
- 请求/响应示例
- 错误处理说明
- 认证和限制说明

### 🕷️ [网页抓取文档](web-scraping.md)
- AmericanBulls.com 抓取策略
- 数据解析实现细节
- 缓存机制说明
- 错误处理和监控

### 🚀 [部署指南](deployment.md)
- Docker 部署方式
- 手动部署步骤
- 生产环境配置
- 监控和维护

## 🛠️ 项目结构总结

您的 Stock Watcher 项目现在具有以下完整结构：

```
stock-watcher/
├── 📄 README.md                    # 项目主要说明文件
├── 🚫 .gitignore                   # Git 忽略规则
├── 📁 docs/                        # 项目文档目录
│   ├── 📄 README.md                # 文档索引（本文件）
│   ├── 📄 project-overview.md      # 项目概述
│   ├── 📄 api-documentation.md     # API 文档
│   ├── 📄 web-scraping.md         # 爬虫文档  
│   └── 📄 deployment.md           # 部署指南
├── 📁 src/                         # 源代码目录
│   ├── 📁 backend/                 # Python FastAPI 后端
│   │   ├── 🐍 app.py               # 主应用程序
│   │   ├── 🗃️ models.py            # 数据模型
│   │   ├── 📋 schemas.py           # API 模式
│   │   ├── 🗃️ db.py                # 数据库配置
│   │   ├── ⏰ scheduler.py         # 定时任务
│   │   ├── 📋 requirements.txt     # Python 依赖
│   │   └── 📁 services/            # 业务服务
│   │       ├── 🌐 americanbulls.py # AB 网站爬虫
│   │       └── 💰 prices.py        # 股价服务
│   ├── 📁 frontend/                # Web 前端
│   │   ├── 📄 index.html           # 主页面
│   │   └── 📁 assets/              # 前端资源
│   │       ├── 🎨 styles.css       # 样式文件
│   │       └── ⚡ app.js           # JavaScript
│   └── 🐳 docker-compose.yml       # Docker 编排
├── 📁 logs/                        # 日志目录
└── 🗃️ stock_watch.db               # SQLite 数据库
```

## 🎯 项目特色

### 已实现功能 ✅
- **实时股价监控** - Yahoo Finance API 集成
- **智能信号抓取** - AmericanBulls.com 自动化抓取
- **响应式仪表盘** - HTML/CSS/JS 前端界面
- **RESTful API** - FastAPI 后端服务
- **定时任务** - 每30分钟自动更新数据
- **数据可视化** - Chart.js 图表展示
- **Docker 支持** - 容器化部署方案

### 技术亮点 🌟
- **模块化架构** - 前后端分离，易于维护
- **智能缓存** - 减少外部 API 调用
- **错误处理** - 完善的异常处理机制
- **文档完整** - 全面的技术文档
- **部署友好** - 支持多种部署方式

## 🚀 快速开始

1. **克隆项目**
   ```bash
   git clone <your-repo-url>
   cd stock-watcher
   ```

2. **启动服务** (Docker 方式)
   ```bash
   docker-compose up -d
   ```

3. **访问应用**
   - 前端界面: http://localhost:3000
   - API 文档: http://localhost:8000/docs

## 📞 获取帮助

- 🐛 **问题反馈**: 请在 GitHub Issues 中提交
- 📖 **使用问题**: 参考对应文档章节
- 🤝 **贡献代码**: 欢迎提交 Pull Request

---

*此项目基于 AmericanBulls.com 数据源，仅供学习和个人使用。*