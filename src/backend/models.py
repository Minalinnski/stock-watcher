from sqlalchemy import Column, Integer, String, DateTime, JSON, Float, UniqueConstraint
from sqlalchemy.sql import func
from .db import Base

class WatchItem(Base):
    __tablename__ = "watchlist"
    id = Column(Integer, primary_key=True)
    symbol = Column(String(16), unique=True, index=True, nullable=False)
    name = Column(String(128), nullable=True)
    display_order = Column(Integer, default=0)  # 显示顺序

class StockQuoteCache(Base):
    __tablename__ = "stock_quote_cache"
    id = Column(Integer, primary_key=True)
    symbol = Column(String(16), index=True, nullable=False)
    price = Column(Float, nullable=True)
    change_pct = Column(Float, nullable=True)
    volume = Column(Integer, nullable=True)
    market_cap = Column(String(32), nullable=True)
    currency = Column(String(8), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (UniqueConstraint('symbol', name='uniq_symbol_quote'),)

class ABSignalCache(Base):
    __tablename__ = "ab_signal_cache"
    id = Column(Integer, primary_key=True)
    symbol = Column(String(16), index=True, nullable=False)
    # 当前建议（比如 STAY LONG / BUY / SELL / SHORT）
    suggestion = Column(String(32), nullable=True)
    # 最近操作历史，扩展到更多条
    signal_history = Column(JSON, nullable=True)
    # 详细摘要信息
    summary = Column(String(2048), nullable=True)
    # 额外的技术指标和信号
    technical_indicators = Column(JSON, nullable=True)
    # 价格目标
    price_target = Column(String(64), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (UniqueConstraint('symbol', name='uniq_symbol_ab'),)
