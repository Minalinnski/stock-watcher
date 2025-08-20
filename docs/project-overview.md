# Stock Watcher - Project Overview

## 项目概述

Stock Watcher 是一个基于 AmericanBulls.com 的股票监控仪表盘，能够自动抓取股票信号和价格数据，提供实时的股票监控和分析功能。

## 核心功能

### 1. 自定义监控列表
- 用户可以添加/删除股票代码到监控列表
- 支持自定义股票名称
- 数据持久化存储

### 2. 实时价格监控
- 集成 Yahoo Finance API 获取实时股价
- 显示当日涨跌幅
- 提供分钟级价格图表

### 3. AmericanBulls 信号抓取
- 自动抓取 AmericanBulls.com 的交易建议
- 获取最近两次 AI 操作记录
- 缓存信号数据，每30分钟更新

### 4. 可视化仪表盘
- 响应式 Web 界面
- 股票表格视图
- 迷你图表预览
- 详细信息弹窗

## 技术架构

### 后端 (Python)
- **Framework**: FastAPI
- **Database**: SQLite with SQLAlchemy ORM
- **Scheduler**: APScheduler for periodic tasks
- **Web Scraping**: BeautifulSoup + Requests
- **Stock Data**: yfinance library

### 前端 (Web)
- **HTML5** + **CSS3** + **Vanilla JavaScript**
- **Chart.js** for data visualization
- **Responsive design** for mobile compatibility

### 部署
- **Docker** containerization
- **Docker Compose** for multi-service orchestration

## 数据流程

```
[Yahoo Finance API] ──→ [Price Service] ──→ [FastAPI Backend]
                                                    ↓
[AmericanBulls.com] ──→ [Scraper Service] ──→ [SQLite Database]
                                                    ↓
[Frontend Dashboard] ←──────────────────── [REST API Endpoints]
```

## 项目结构

```
stock-watcher/
├── src/
│   ├── backend/          # Python FastAPI backend
│   │   ├── services/     # Business logic services
│   │   ├── models.py     # Database models
│   │   ├── schemas.py    # Pydantic schemas
│   │   └── app.py        # Main application
│   ├── frontend/         # Web frontend
│   │   ├── assets/       # CSS, JS files
│   │   └── index.html    # Main HTML page
│   └── docker-compose.yml
├── docs/                 # Project documentation
├── logs/                 # Application logs
└── README.md            # Setup instructions
```

## 主要特性

1. **自动化监控**: 后台定时任务自动更新股票信号
2. **实时数据**: 集成多个数据源提供准确的市场信息  
3. **智能缓存**: 减少外部 API 调用，提高响应速度
4. **用户友好**: 简洁的界面设计，支持移动端访问
5. **可扩展性**: 模块化设计，易于添加新功能

## 使用场景

- 个人股票投资监控
- 快速查看 AmericanBulls 信号推荐
- 多股票组合的集中管理
- 实时价格追踪和图表分析