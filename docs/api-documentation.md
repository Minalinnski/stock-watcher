# API Documentation

## Base URL
```
http://localhost:8000
```

## Endpoints

### Watchlist Management

#### GET /api/watchlist
获取用户监控列表中的所有股票

**Response:**
```json
[
    {
        "symbol": "AAPL",
        "name": "Apple Inc."
    },
    {
        "symbol": "MSFT", 
        "name": "Microsoft Corporation"
    }
]
```

#### POST /api/watchlist
添加股票到监控列表

**Request Body:**
```json
{
    "symbol": "AAPL",
    "name": "Apple Inc."
}
```

**Response:**
```json
{
    "symbol": "AAPL",
    "name": "Apple Inc."
}
```

#### DELETE /api/watchlist/{symbol}
从监控列表中删除指定股票

**Parameters:**
- `symbol` (string): 股票代码

**Response:**
```json
{
    "ok": true
}
```

### American Bulls Signals

#### GET /api/ab/{symbol}
获取指定股票的 AmericanBulls 信号数据

**Parameters:**
- `symbol` (string): 股票代码

**Response:**
```json
{
    "symbol": "AAPL",
    "suggestion": "STAY LONG",
    "last_two_actions": [
        {
            "date": "2025-08-15",
            "signal": "BUY"
        },
        {
            "date": "2025-08-10", 
            "signal": "SELL"
        }
    ],
    "summary": "技术指标显示持续上涨趋势，建议持有多头仓位...",
    "updated_at": "2025-08-20T10:30:00Z"
}
```

### Stock Quotes

#### GET /api/quote/{symbol}
获取股票实时报价

**Parameters:**
- `symbol` (string): 股票代码

**Response:**
```json
{
    "symbol": "AAPL",
    "price": 226.50,
    "change": 1.45,
    "currency": "USD"
}
```

### Stock Charts

#### GET /api/chart/{symbol}
获取股票图表数据

**Parameters:**
- `symbol` (string): 股票代码
- `period` (string, optional): 时间周期，默认 "1d"
- `interval` (string, optional): 数据间隔，默认 "1m"

**Response:**
```json
{
    "symbol": "AAPL",
    "points": [
        {
            "t": 1724142600000,
            "p": 225.32
        },
        {
            "t": 1724142660000,
            "p": 225.41
        }
    ]
}
```

## Error Responses

所有错误响应遵循以下格式：

```json
{
    "detail": "Error message description"
}
```

### HTTP Status Codes

- `200`: Success
- `400`: Bad Request - 请求参数错误
- `404`: Not Found - 资源不存在
- `500`: Internal Server Error - 服务器内部错误

## Rate Limiting

- Yahoo Finance API: 建议限制在每分钟 100 次请求
- AmericanBulls 爬虫: 建议每个股票每小时不超过 1 次请求

## Authentication

当前版本不需要身份验证，但在生产环境中建议添加 API Key 或 OAuth 认证。

## CORS

API 支持跨域请求，可通过环境变量 `CORS_ORIGINS` 配置允许的域名：

```bash
CORS_ORIGINS="http://localhost:3000,https://yourdomain.com"
```