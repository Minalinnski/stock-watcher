from pydantic import BaseModel, Field
from typing import List, Optional, Any

class WatchCreate(BaseModel):
    symbol: str
    name: Optional[str] = None

class WatchItemOut(BaseModel):
    symbol: str
    name: Optional[str] = None

class ABAction(BaseModel):
    date: str
    signal: str

class ABSignalOut(BaseModel):
    symbol: str
    suggestion: Optional[str]
    last_two_actions: List[ABAction] = Field(default_factory=list)
    summary: Optional[str] = None
    updated_at: Optional[str] = None

class QuoteOut(BaseModel):
    symbol: str
    price: Optional[float]
    change: Optional[float]     # 当日涨跌百分比（如 1.23 表示 +1.23%）
    currency: Optional[str] = None

class SparkPoint(BaseModel):
    t: int
    p: float

class ChartOut(BaseModel):
    symbol: str
    points: List[SparkPoint]
