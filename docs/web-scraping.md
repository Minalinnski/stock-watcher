# Web Scraping Documentation

## AmericanBulls.com 数据抓取

### 目标网站
- **Base URL**: `https://www.americanbulls.com/SignalPage.aspx?lang=en&Ticker={symbol}`
- **示例**: https://www.americanbulls.com/SignalPage.aspx?lang=en&Ticker=AAPL

### 抓取策略

#### 1. HTTP 请求配置
```python
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; WatchABBot/1.0; +https://example.com/bot)"
}
```

#### 2. 数据解析目标

##### a) 交易建议 (Suggestion)
- **位置**: 页面顶部大标题区域
- **可能值**: `BUY`, `SELL`, `SHORT`, `STAY LONG`
- **解析方法**: 搜索页面中匹配预定义关键词的文本

##### b) 信号更新摘要 (Signal Update)
- **位置**: "Signal Update" 标题下方的段落
- **内容**: 技术分析描述和市场建议
- **解析方法**: 查找包含 "Signal Update" 的文本，获取后续段落内容

##### c) 历史信号记录 (Signal History)
- **位置**: "Signal History" 表格
- **数据结构**: 
  ```
  Date | Price | Signal
  ```
- **获取**: 最近两条记录的日期和信号类型

### 实现细节

#### 核心函数: `fetch_ab_for_symbol(symbol)`

```python
def fetch_ab_for_symbol(symbol: str):
    url = BASE.format(symbol=symbol.upper())
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    
    suggestion, summary = parse_suggestion_and_update(soup)
    last_two = parse_signal_history(soup)
    
    return {
        "symbol": symbol.upper(),
        "suggestion": suggestion,
        "summary": summary,
        "last_two_actions": last_two,
    }
```

#### 建议解析: `parse_suggestion_and_update(soup)`
1. 遍历页面所有文本节点
2. 查找匹配预定义关键词的内容
3. 定位 "Signal Update" 段落并提取摘要

#### 历史记录解析: `parse_signal_history(soup)`
1. 查找包含 "Signal History" 的标题元素
2. 定位后续的表格元素
3. 提取前两行数据（跳过表头）
4. 解析日期和信号类型

### 数据缓存策略

#### 缓存表结构 (ABSignalCache)
```sql
CREATE TABLE ab_signal_cache (
    id INTEGER PRIMARY KEY,
    symbol VARCHAR(16) NOT NULL,
    suggestion VARCHAR(32),
    last_two_actions JSON,
    summary VARCHAR(1024),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol)
);
```

#### 更新频率
- **自动更新**: 每 30 分钟通过 APScheduler 执行
- **即时更新**: API 请求时如果缓存不存在则立即抓取
- **缓存有效期**: 30 分钟内的数据视为有效

### 错误处理

#### 网络错误
```python
try:
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
except requests.RequestException as e:
    # 记录错误日志
    # 返回缓存数据或默认值
```

#### 解析错误
- HTML 结构变化导致的解析失败
- 数据格式不符合预期
- 空数据处理

### 遵循网站规则

#### 请求频率限制
- **建议频率**: 每个股票每小时不超过 1 次请求
- **并发限制**: 避免同时发送大量请求
- **用户代理**: 使用标识性的 User-Agent

#### Robots.txt 遵循
- 检查网站的 robots.txt 文件
- 遵循爬取限制和延迟要求

### 监控和日志

#### 抓取统计
- 成功/失败请求数量
- 响应时间监控
- 数据质量检查

#### 异常情况
- HTTP 错误状态码
- 解析失败的页面
- 数据结构变化警告

### 扩展性考虑

#### 多数据源支持
- 可扩展到其他财经网站
- 统一的数据格式接口
- 配置化的抓取规则

#### 反爬虫应对
- IP 轮换机制
- 随机请求间隔
- 代理服务器支持