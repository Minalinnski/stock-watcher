import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, delete, update, func
from .db import Base, engine, SessionLocal
from .models import WatchItem, ABSignalCache, StockQuoteCache
from .schemas import WatchCreate, WatchItemOut, ABSignalOut, QuoteOut, ChartOut
from .services.prices import get_quote, get_intraday_points, validate_symbol
from .scheduler import create_scheduler
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AB Watch Dashboard")

# 静态文件服务 - 前后端一体化
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

# CORS (现在主要用于开发)
origins = os.getenv("CORS_ORIGINS","").split(",") if os.getenv("CORS_ORIGINS") else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化 DB
Base.metadata.create_all(bind=engine)
scheduler = create_scheduler()
scheduler.start()

@app.on_event("shutdown")
def on_shutdown():
    scheduler.shutdown(wait=False)

# ---- Watchlist CRUD ----
@app.get("/api/watchlist", response_model=list[WatchItemOut])
def list_watchlist():
    db = SessionLocal()
    try:
        items = db.execute(select(WatchItem)).scalars().all()
        return [{"symbol": w.symbol, "name": w.name} for w in items]
    finally:
        db.close()

@app.post("/api/watchlist", response_model=WatchItemOut)
def add_watch(item: WatchCreate):
    sym = item.symbol.upper().strip()
    if not sym:
        raise HTTPException(400, "symbol required")
    
    # 验证股票代码
    if not validate_symbol(sym):
        raise HTTPException(400, f"Invalid stock symbol: {sym}")
    
    db = SessionLocal()
    try:
        exists = db.execute(select(WatchItem).where(WatchItem.symbol==sym)).scalar_one_or_none()
        if exists:
            return {"symbol": exists.symbol, "name": exists.name}
        
        # 获取最大排序值
        max_order = db.execute(select(func.max(WatchItem.display_order))).scalar() or 0
        
        obj = WatchItem(symbol=sym, name=item.name, display_order=max_order + 1)
        db.add(obj)
        db.commit()
        return {"symbol": sym, "name": item.name}
    finally:
        db.close()

@app.delete("/api/watchlist/{symbol}")
def del_watch(symbol: str):
    db = SessionLocal()
    try:
        db.execute(delete(WatchItem).where(WatchItem.symbol==symbol.upper()))
        db.execute(delete(ABSignalCache).where(ABSignalCache.symbol==symbol.upper()))
        db.execute(delete(StockQuoteCache).where(StockQuoteCache.symbol==symbol.upper()))
        db.commit()
        return {"ok": True}
    finally:
        db.close()

@app.put("/api/watchlist/reorder")
def reorder_watchlist(order_data: list[dict]):
    """更新监控列表的显示顺序"""
    db = SessionLocal()
    try:
        for item in order_data:
            symbol = item.get("symbol", "").upper()
            order = item.get("order", 0)
            if symbol:
                db.execute(
                    update(WatchItem).where(WatchItem.symbol == symbol).values(display_order=order)
                )
        db.commit()
        return {"ok": True}
    finally:
        db.close()

# ---- AB Signals ----
@app.get("/api/ab/{symbol}", response_model=ABSignalOut)
def get_ab(symbol: str):
    db = SessionLocal()
    try:
        obj = db.execute(select(ABSignalCache).where(ABSignalCache.symbol==symbol.upper())).scalar_one_or_none()
        if not obj:
            # 未缓存则尝试即时抓一次
            from .services.americanbulls import fetch_ab_for_symbol
            data = fetch_ab_for_symbol(symbol)
            obj = ABSignalCache(
                symbol=symbol.upper(), 
                suggestion=data.get("suggestion"),
                signal_history=data.get("signal_history", []),
                summary=data.get("summary"),
                technical_indicators=data.get("technical_indicators", {}),
                price_target=data.get("price_target")
            )
            db.add(obj); db.commit(); db.refresh(obj)
        
        # 兼容旧版本API字段
        last_two_actions = (obj.signal_history or [])[:2] if obj.signal_history else []
        
        return {
            "symbol": obj.symbol,
            "suggestion": obj.suggestion,
            "signal_history": obj.signal_history or [],
            "last_two_actions": last_two_actions,  # 保持向后兼容
            "summary": obj.summary,
            "technical_indicators": obj.technical_indicators or {},
            "price_target": obj.price_target,
            "updated_at": obj.updated_at.isoformat() if obj.updated_at else None
        }
    finally:
        db.close()

# ---- Quotes ----
@app.get("/api/quote/{symbol}", response_model=QuoteOut)
def api_quote(symbol: str):
    return get_quote(symbol)

@app.get("/api/chart/{symbol}", response_model=ChartOut)
def api_chart(symbol: str, period: str="1d", interval: str="1m"):
    return get_intraday_points(symbol, period=period, interval=interval)
