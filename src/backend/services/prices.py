import yfinance as yf
import requests
import time
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# 缓存和限流控制
_last_request_time = {}
_request_cache = {}
MIN_REQUEST_INTERVAL = 2  # 最少2秒间隔

def _wait_for_rate_limit(symbol: str):
    """确保请求间隔，避免频率限制"""
    now = time.time()
    last_time = _last_request_time.get(symbol, 0)
    if now - last_time < MIN_REQUEST_INTERVAL:
        time.sleep(MIN_REQUEST_INTERVAL - (now - last_time))
    _last_request_time[symbol] = time.time()

def validate_symbol(symbol: str) -> bool:
    """验证股票代码是否有效"""
    try:
        symbol = symbol.upper().strip()
        if not symbol or len(symbol) > 10:
            return False
        
        # 简单的格式检查
        if not symbol.isalnum() and '.' not in symbol:
            return False
            
        # 尝试获取基本信息验证
        _wait_for_rate_limit(symbol)
        t = yf.Ticker(symbol)
        info = t.fast_info
        
        # 检查是否有有效的价格数据
        if info.last_price is not None and info.last_price > 0:
            return True
        return False
    except Exception as e:
        logger.warning(f"Symbol validation failed for {symbol}: {e}")
        return False

def get_quote(symbol: str) -> Dict[str, Any]:
    """获取股票报价，带缓存和错误处理"""
    symbol = symbol.upper()
    
    # 检查缓存（5分钟有效期）
    cache_key = f"quote_{symbol}"
    cached = _request_cache.get(cache_key)
    if cached and (time.time() - cached['timestamp']) < 300:  # 5分钟缓存
        return cached['data']
    
    try:
        _wait_for_rate_limit(symbol)
        t = yf.Ticker(symbol)
        
        # 优先使用 fast_info，失败则使用历史数据
        result = {"symbol": symbol, "price": None, "change": None, "currency": None, "volume": None}
        
        try:
            info = t.fast_info
            if info.last_price is not None:
                result["price"] = round(float(info.last_price), 2)
                result["currency"] = getattr(info, "currency", "USD")
        except:
            pass
        
        # 如果 fast_info 失败，尝试历史数据
        if result["price"] is None:
            try:
                # 使用更宽松的时间范围
                hist = t.history(period="2d", interval="1d")  # 改为日线数据
                if not hist.empty:
                    latest = hist.iloc[-1]
                    result["price"] = round(float(latest["Close"]), 2)
                    
                    # 计算涨跌幅
                    if len(hist) >= 2:
                        prev_close = hist.iloc[-2]["Close"]
                        if prev_close > 0:
                            result["change"] = round((result["price"] / prev_close - 1) * 100, 2)
                    
                    result["volume"] = int(latest["Volume"]) if latest["Volume"] > 0 else None
            except Exception as e:
                logger.warning(f"Failed to get history for {symbol}: {e}")
        
        # 缓存结果
        _request_cache[cache_key] = {
            'data': result,
            'timestamp': time.time()
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get quote for {symbol}: {e}")
        # 返回缓存的数据（如果有）
        if cached:
            return cached['data']
        return {"symbol": symbol, "price": None, "change": None, "currency": None, "volume": None}

def get_intraday_points(symbol: str, period="1d", interval="5m") -> Dict[str, Any]:
    """获取图表数据，使用更宽松的间隔"""
    symbol = symbol.upper()
    
    # 检查缓存（10分钟有效期）
    cache_key = f"chart_{symbol}_{period}_{interval}"
    cached = _request_cache.get(cache_key)
    if cached and (time.time() - cached['timestamp']) < 600:  # 10分钟缓存
        return cached['data']
    
    try:
        _wait_for_rate_limit(symbol)
        t = yf.Ticker(symbol)
        
        # 使用更保守的参数避免频率限制
        hist = t.history(period=period, interval=interval)
        pts = []
        
        if not hist.empty:
            for ts, row in hist.iterrows():
                try:
                    # 转毫秒时间戳
                    t_ms = int(ts.timestamp() * 1000)
                    price = round(float(row["Close"]), 4)
                    pts.append({"t": t_ms, "p": price})
                except:
                    continue
        
        result = {"symbol": symbol, "points": pts}
        
        # 缓存结果
        _request_cache[cache_key] = {
            'data': result,
            'timestamp': time.time()
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get chart data for {symbol}: {e}")
        # 返回缓存的数据或空数据
        if cached:
            return cached['data']
        return {"symbol": symbol, "points": []}
