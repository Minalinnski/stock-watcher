import yfinance as yf
from datetime import datetime, timezone

def get_quote(symbol: str):
    t = yf.Ticker(symbol)
    info = t.fast_info  # 快速字段
    price = None
    change_pct = None
    currency = None
    try:
        price = float(info.last_price) if info.last_price is not None else None
        # fast_info 没有当日涨跌百分比，换用 recent data 估算
        hist = t.history(period="1d", interval="1m")
        if not hist.empty:
            open0 = hist["Close"].iloc[0]
            last = hist["Close"].iloc[-1]
            if open0 and last:
                change_pct = round((last / open0 - 1) * 100, 2)
            price = float(last)
        currency = getattr(info, "currency", None)
    except Exception:
        pass
    return {"symbol": symbol.upper(), "price": price, "change": change_pct, "currency": currency}

def get_intraday_points(symbol: str, period="1d", interval="1m"):
    t = yf.Ticker(symbol)
    hist = t.history(period=period, interval=interval)
    pts = []
    if not hist.empty:
        for ts, row in hist.iterrows():
            # 转毫秒时间戳（UTC）
            t_ms = int(datetime.fromtimestamp(ts.timestamp(), tz=timezone.utc).timestamp() * 1000)
            pts.append({"t": t_ms, "p": round(float(row["Close"]), 4)})
    return {"symbol": symbol.upper(), "points": pts}
