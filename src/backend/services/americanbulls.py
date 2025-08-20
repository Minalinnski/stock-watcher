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
SEARCH_BASE = "https://www.americanbulls.com/SearchList.aspx?lang=en&SearchText={symbol}"

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

def validate_symbol_and_get_name(symbol: str) -> Dict[str, Any]:
    """使用AmericanBulls验证股票代码并获取公司名称"""
    symbol = symbol.upper().strip()
    
    try:
        # 首先尝试直接访问股票页面
        url = BASE.format(symbol=symbol)
        response = requests.get(url, headers=HEADERS, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            # 检查页面是否包含有效的股票信息
            page_text = soup.get_text()
            
            # 检查页面是否包含股票特征信息
            has_stock_info = any([
                symbol in page_text.upper(),
                "STAY LONG" in page_text,
                "BUY" in page_text,
                "SELL" in page_text,
                "Close" in page_text and "Prev.Close" in page_text,
                "NASDAQ" in page_text or "NYSE" in page_text or "AMEX" in page_text
            ])
            
            if not has_stock_info or len(page_text) < 10000:
                # 页面没有股票信息或内容太少
                logger.warning(f"Invalid stock page for {symbol}, content length: {len(page_text)}")
                return {"valid": False, "symbol": symbol, "name": None}
            
            # 尝试提取公司名称
            company_name = extract_company_name(soup, symbol)
            
            logger.info(f"Symbol {symbol} validated successfully via direct access")
            return {
                "valid": True,
                "symbol": symbol,
                "name": company_name
            }
            
    except requests.RequestException as e:
        logger.warning(f"Direct access failed for {symbol}: {e}")
    
    # 如果直接访问失败，尝试搜索
    try:
        search_url = SEARCH_BASE.format(symbol=symbol)
        response = requests.get(search_url, headers=HEADERS, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            # 检查搜索结果
            search_results = parse_search_results(soup, symbol)
            
            if search_results:
                logger.info(f"Symbol {symbol} found via search")
                return {
                    "valid": True,
                    "symbol": symbol,
                    "name": search_results.get("name")
                }
            else:
                logger.info(f"Symbol {symbol} not found in search results")
                return {"valid": False, "symbol": symbol, "name": None}
                
    except requests.RequestException as e:
        logger.error(f"Search failed for {symbol}: {e}")
        return {"valid": False, "symbol": symbol, "name": None}
    
    return {"valid": False, "symbol": symbol, "name": None}

def extract_company_name(soup, symbol: str) -> Optional[str]:
    """从股票页面提取公司名称"""
    try:
        page_text = soup.get_text()
        
        # 方法1: 从页面文本中查找公司名称模式
        # 基于观察到的结构：AAPL (NASDAQ) 后面跟着 Apple Inc
        lines = [line.strip() for line in page_text.split('\n') if line.strip()]
        
        for i, line in enumerate(lines):
            # 查找包含股票代码和交易所的行，格式如 "AAPL  NASDAQ"
            if (symbol in line and 
                any(exchange in line for exchange in ['NASDAQ', 'NYSE', 'AMEX']) and
                len(line.split()) <= 3):  # 避免匹配到其他包含代码的长行
                
                # 检查下一行是否是公司名称
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    
                    # 过滤掉常见的页面元素和信号
                    excluded_phrases = [
                        'Cookie Consent', 'Privacy Policy', 'americanbulls', 'Register', 'Sign In',
                        'STAY LONG', 'BUY', 'SELL', 'SHORT', 'Close', 'Open', 'High', 'Low',
                        'Prev.Close', 'Change', 'Change%', 'Volume', 'EN', 'English'
                    ]
                    
                    # 公司名称的特征：长度合适，不是数字，不是排除的短语
                    if (3 < len(next_line) < 100 and 
                        next_line != symbol and 
                        not next_line.replace('.', '').replace('-', '').isdigit() and
                        not any(phrase.lower() in next_line.lower() for phrase in excluded_phrases)):
                        
                        logger.info(f"Found company name for {symbol}: {next_line}")
                        return next_line
        
        # 方法2: 从标题提取
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text().strip()
            # 标题格式如 "AAPL (NASDAQ)"
            if symbol in title and "(" in title:
                # 有时候标题之后会有公司名
                title_clean = title.replace(f"{symbol}", "").replace("(NASDAQ)", "").replace("(NYSE)", "").replace("(AMEX)", "").strip()
                if title_clean and len(title_clean) > 3:
                    return title_clean
        
        # 方法3: 查找包含常见公司后缀的文本
        company_suffixes = ['Inc', 'Corp', 'Corporation', 'Company', 'Co', 'Ltd', 'LLC', 'Technologies', 'Systems']
        for line in lines:
            line_clean = line.strip()
            if (any(suffix in line_clean for suffix in company_suffixes) and 
                symbol not in line_clean and 
                len(line_clean) > 5 and len(line_clean) < 100):
                return line_clean
        
        # 方法4: 查找位于股票代码附近的可能的公司名
        text_parts = page_text.split()
        for i, part in enumerate(text_parts):
            if part == symbol:
                # 查看前后几个词
                for offset in [1, 2, 3, -1, -2, -3]:
                    if 0 <= i + offset < len(text_parts):
                        candidate = text_parts[i + offset]
                        if (len(candidate) > 3 and 
                            candidate not in ['NASDAQ', 'NYSE', 'AMEX', 'Close', 'Open', 'High', 'Low'] and
                            not candidate.replace('.', '').isdigit()):
                            # 可能找到了公司名的一部分，尝试获取更多上下文
                            start = max(0, i + offset - 2)
                            end = min(len(text_parts), i + offset + 3)
                            context = ' '.join(text_parts[start:end])
                            if len(context) > 5 and len(context) < 100:
                                return context.strip()
        
        return None
        
    except Exception as e:
        logger.warning(f"Failed to extract company name for {symbol}: {e}")
        return None

def parse_search_results(soup, target_symbol: str) -> Optional[Dict[str, str]]:
    """解析搜索结果页面"""
    try:
        # 查找搜索结果表格或列表
        # 根据实际页面结构调整选择器
        
        # 方法1: 查找包含股票代码的链接
        links = soup.find_all("a", href=re.compile(r"SignalPage.*Ticker=", re.I))
        
        for link in links:
            href = link.get("href", "")
            link_text = link.get_text().strip()
            
            # 检查链接是否包含目标股票代码
            if target_symbol.upper() in href.upper() or target_symbol.upper() in link_text.upper():
                # 尝试提取公司名称
                # 搜索结果通常格式如 "AAPL - Apple Inc."
                if " - " in link_text:
                    parts = link_text.split(" - ")
                    if len(parts) >= 2:
                        return {
                            "symbol": target_symbol,
                            "name": parts[1].strip()
                        }
                
                # 或者从父元素中查找名称
                parent = link.find_parent()
                if parent:
                    parent_text = parent.get_text()
                    if target_symbol in parent_text:
                        # 简单的名称提取逻辑
                        clean_text = parent_text.replace(target_symbol, "").strip()
                        if clean_text and len(clean_text) > 3:
                            return {
                                "symbol": target_symbol,
                                "name": clean_text[:100]
                            }
        
        # 方法2: 查找表格行
        rows = soup.find_all("tr")
        for row in rows:
            row_text = row.get_text()
            if target_symbol.upper() in row_text.upper():
                cells = row.find_all(["td", "th"])
                if len(cells) >= 2:
                    # 通常第一列是代码，第二列是名称
                    symbol_cell = cells[0].get_text().strip()
                    name_cell = cells[1].get_text().strip()
                    
                    if target_symbol.upper() in symbol_cell.upper():
                        return {
                            "symbol": target_symbol,
                            "name": name_cell
                        }
        
        return None
        
    except Exception as e:
        logger.warning(f"Failed to parse search results for {target_symbol}: {e}")
        return None
