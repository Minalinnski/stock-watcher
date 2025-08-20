from sqlalchemy import Column, Integer, String, DateTime, JSON, UniqueConstraint
from sqlalchemy.sql import func
from .db import Base

class WatchItem(Base):
    __tablename__ = "watchlist"
    id = Column(Integer, primary_key=True)
    symbol = Column(String(16), unique=True, index=True, nullable=False)
    name = Column(String(128), nullable=True)

class ABSignalCache(Base):
    __tablename__ = "ab_signal_cache"
    id = Column(Integer, primary_key=True)
    symbol = Column(String(16), index=True, nullable=False)
    # 当前建议（比如 STAY LONG / BUY / SELL / SHORT）
    suggestion = Column(String(32), nullable=True)
    # 最近两次操作，如 [{"date":"2025-08-08","signal":"BUY"}, {"date":"2025-08-01","signal":"SELL"}]
    last_two_actions = Column(JSON, nullable=True)
    # 其他摘要信息（如上一信号的描述/涨跌幅/文本）
    summary = Column(String(1024), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (UniqueConstraint('symbol', name='uniq_symbol_ab'),)
