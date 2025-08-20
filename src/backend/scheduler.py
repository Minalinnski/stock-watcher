import os
import logging
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select
from .db import SessionLocal
from .models import WatchItem, ABSignalCache, StockQuoteCache
from .services.americanbulls import fetch_ab_for_symbol
from .services.prices import get_quote

logger = logging.getLogger(__name__)

def refresh_ab_signals():
    """刷新AmericanBulls信号数据"""
    logger.info("Starting AB signals refresh...")
    db = SessionLocal()
    try:
        symbols = [w.symbol for w in db.execute(select(WatchItem)).scalars().all()]
        logger.info(f"Refreshing AB signals for {len(symbols)} symbols")
        
        for sym in symbols:
            try:
                logger.info(f"Fetching AB data for {sym}")
                data = fetch_ab_for_symbol(sym)
                
                # 查找或创建缓存记录
                obj = db.execute(select(ABSignalCache).where(ABSignalCache.symbol==sym)).scalar_one_or_none()
                if not obj:
                    obj = ABSignalCache(symbol=sym)
                    db.add(obj)
                
                # 更新所有字段
                obj.suggestion = data.get("suggestion")
                obj.summary = data.get("summary")
                obj.signal_history = data.get("signal_history", [])
                obj.technical_indicators = data.get("technical_indicators", {})
                obj.price_target = data.get("price_target")
                
                # 添加延时避免过于频繁的请求
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Failed to refresh AB data for {sym}: {e}")
                continue
        
        db.commit()
        logger.info("AB signals refresh completed")
        
    except Exception as e:
        logger.error(f"AB signals refresh failed: {e}")
        db.rollback()
    finally:
        db.close()

def refresh_stock_quotes():
    """刷新股票报价数据"""
    logger.info("Starting stock quotes refresh...")
    db = SessionLocal()
    try:
        symbols = [w.symbol for w in db.execute(select(WatchItem)).scalars().all()]
        logger.info(f"Refreshing quotes for {len(symbols)} symbols")
        
        for sym in symbols:
            try:
                quote_data = get_quote(sym)
                
                # 查找或创建报价缓存记录
                obj = db.execute(select(StockQuoteCache).where(StockQuoteCache.symbol==sym)).scalar_one_or_none()
                if not obj:
                    obj = StockQuoteCache(symbol=sym)
                    db.add(obj)
                
                # 更新报价数据
                obj.price = quote_data.get("price")
                obj.change_pct = quote_data.get("change")
                obj.volume = quote_data.get("volume")
                obj.currency = quote_data.get("currency", "USD")
                
            except Exception as e:
                logger.error(f"Failed to refresh quote for {sym}: {e}")
                continue
        
        db.commit()
        logger.info("Stock quotes refresh completed")
        
    except Exception as e:
        logger.error(f"Stock quotes refresh failed: {e}")
        db.rollback()
    finally:
        db.close()

def create_scheduler():
    """创建后台调度器，分别设置AB信号和股价的更新频率"""
    
    # AB 信号更新频率（默认60分钟）
    ab_interval_min = int(os.getenv("AB_SCRAPE_INTERVAL_MIN", "60"))
    
    # 股价更新频率（默认10分钟）  
    quote_interval_min = int(os.getenv("QUOTE_REFRESH_INTERVAL_MIN", "10"))
    
    timezone = os.getenv("TZ", "UTC")
    sched = BackgroundScheduler(timezone=timezone)
    
    # 添加AB信号刷新任务
    sched.add_job(
        refresh_ab_signals, 
        IntervalTrigger(minutes=ab_interval_min), 
        id="ab_signals_refresh", 
        replace_existing=True,
        max_instances=1  # 防止重叠执行
    )
    
    # 添加股价刷新任务
    sched.add_job(
        refresh_stock_quotes, 
        IntervalTrigger(minutes=quote_interval_min), 
        id="stock_quotes_refresh", 
        replace_existing=True,
        max_instances=1
    )
    
    logger.info(f"Scheduler created: AB signals every {ab_interval_min}min, quotes every {quote_interval_min}min")
    return sched
