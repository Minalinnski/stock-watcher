import re
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
import logging
import time

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

BASE = "https://www.americanbulls.com/SignalPage.aspx?lang=en&Ticker={symbol}"

def parse_signal_history(soup) -> List[Dict[str, str]]:
    """从 'Signal History' 表格抓取更多历史记录"""
    history = []
    
    try:
        # 尝试多种方式找到信号历史表格
        table = None
        
        # 方法1: 查找包含 "Signal History" 的文本
        header = soup.find(string=re.compile(r"Signal History", re.I))
        if header:
            table = header.find_parent().find_next("table")
        
        # 方法2: 查找包含日期模式的表格
        if not table:
            tables = soup.find_all("table")
            for t in tables:
                rows = t.find_all("tr")
                if len(rows) > 1:
                    first_row_text = rows[1].get_text()
                    # 查找日期模式 (MM/DD/YYYY 或 YYYY-MM-DD)
                    if re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2}', first_row_text):
                        table = t
                        break
        
        if table:
            rows = table.find_all("tr")
            # 跳过表头，获取更多历史记录（最多8条）
            for tr in rows[1:9]:
                tds = [td.get_text(strip=True) for td in tr.find_all("td")]
                if len(tds) >= 3:
                    date = tds[0]
                    price = tds[1] if len(tds) > 1 else ""
                    signal = tds[2].upper() if len(tds) > 2 else ""
                    
                    # 清理信号文本
                    signal = re.sub(r'[^\w\s]', '', signal).strip()
                    
                    if date and signal:
                        history.append({
                            "date": date,
                            "price": price,
                            "signal": signal
                        })
                        
    except Exception as e:
        logger.warning(f"Failed to parse signal history: {e}")
    
    return history

def parse_suggestion_and_details(soup) -> tuple:
    """解析建议和详细信息，包括技术指标"""
    suggestion = None
    summary = None
    technical_indicators = {}
    price_target = None
    
    try:
        # 查找当前建议 - 尝试多种模式
        suggestion_patterns = [
            r'\b(BUY|SELL|SHORT|STAY LONG|HOLD|STRONG BUY|STRONG SELL)\b',
            r'Current Signal:\s*([A-Z\s]+)',
            r'Recommendation:\s*([A-Z\s]+)'
        ]
        
        page_text = soup.get_text()
        for pattern in suggestion_patterns:
            match = re.search(pattern, page_text, re.I)
            if match:
                suggestion = match.group(1).upper().strip()
                break
        
        # 查找 Signal Update 或相关描述
        update_patterns = [
            r"Signal Update",
            r"Analysis",
            r"Commentary",
            r"Market View"
        ]
        
        for pattern in update_patterns:
            su = soup.find(string=re.compile(pattern, re.I))
            if su:
                # 获取后续的段落文本
                parent = su.find_parent()
                if parent:
                    next_elements = parent.find_next_siblings(["p", "div", "span"])
                    if next_elements:
                        summary = next_elements[0].get_text(" ", strip=True)[:500]  # 限制长度
                        break
        
        # 尝试解析技术指标
        tech_indicators_text = soup.get_text()
        
        # 查找RSI
        rsi_match = re.search(r'RSI[:\s]*(\d+\.?\d*)', tech_indicators_text, re.I)
        if rsi_match:
            technical_indicators['RSI'] = float(rsi_match.group(1))
        
        # 查找移动平均线信号
        ma_patterns = [
            (r'MA\s*(\d+)[:\s]*([A-Z]+)', 'MA_Signal'),
            (r'Moving Average[:\s]*([A-Z]+)', 'MA_Signal'),
            (r'(\d+)-day MA[:\s]*([A-Z]+)', 'MA_Signal')
        ]
        
        for pattern, key in ma_patterns:
            ma_match = re.search(pattern, tech_indicators_text, re.I)
            if ma_match:
                if len(ma_match.groups()) >= 2:
                    technical_indicators[key] = ma_match.group(2).upper()
                else:
                    technical_indicators[key] = ma_match.group(1).upper()
                break
        
        # 查找价格目标
        price_patterns = [
            r'Target[:\s]*\$?(\d+\.?\d*)',
            r'Price Target[:\s]*\$?(\d+\.?\d*)',
            r'Objective[:\s]*\$?(\d+\.?\d*)'
        ]
        
        for pattern in price_patterns:
            price_match = re.search(pattern, tech_indicators_text, re.I)
            if price_match:
                price_target = f"${price_match.group(1)}"
                break
                
    except Exception as e:
        logger.warning(f"Failed to parse suggestion and details: {e}")
    
    return suggestion, summary, technical_indicators, price_target

def fetch_ab_for_symbol(symbol: str) -> Dict[str, Any]:
    """获取AmericanBulls的完整分析数据"""
    symbol = symbol.upper()
    url = BASE.format(symbol=symbol)
    
    try:
        # 添加请求间隔，避免被限制
        time.sleep(1)
        
        response = requests.get(url, headers=HEADERS, timeout=20)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 解析各种数据
        suggestion, summary, technical_indicators, price_target = parse_suggestion_and_details(soup)
        signal_history = parse_signal_history(soup)
        
        result = {
            "symbol": symbol,
            "suggestion": suggestion,
            "summary": summary,
            "signal_history": signal_history,
            "technical_indicators": technical_indicators,
            "price_target": price_target,
            "data_source": "americanbulls.com",
            "scraped_at": time.time()
        }
        
        logger.info(f"Successfully fetched AB data for {symbol}: {len(signal_history)} signals, suggestion: {suggestion}")
        return result
        
    except requests.RequestException as e:
        logger.error(f"Network error fetching AB data for {symbol}: {e}")
        return {
            "symbol": symbol,
            "suggestion": None,
            "summary": f"网络错误: {str(e)[:100]}",
            "signal_history": [],
            "technical_indicators": {},
            "price_target": None,
            "error": str(e)
        }
    except Exception as e:
        logger.error(f"Unexpected error fetching AB data for {symbol}: {e}")
        return {
            "symbol": symbol,
            "suggestion": None,
            "summary": f"解析错误: {str(e)[:100]}",
            "signal_history": [],
            "technical_indicators": {},
            "price_target": None,
            "error": str(e)
        }
