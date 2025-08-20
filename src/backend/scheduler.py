import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select
from .db import SessionLocal
from .models import WatchItem, ABSignalCache
from .services.americanbulls import fetch_ab_for_symbol

def refresh_ab_for_all():
    db = SessionLocal()
    try:
        symbols = [w.symbol for w in db.execute(select(WatchItem)).scalars().all()]
        for sym in symbols:
            data = fetch_ab_for_symbol(sym)
            obj = db.query(ABSignalCache).filter(ABSignalCache.symbol==sym).one_or_none()
            if not obj:
                obj = ABSignalCache(symbol=sym)
                db.add(obj)
            obj.suggestion = data.get("suggestion")
            obj.summary = data.get("summary")
            obj.last_two_actions = data.get("last_two_actions") or []
        db.commit()
    finally:
        db.close()

def create_scheduler():
    interval_min = int(os.getenv("AB_SCRAPE_INTERVAL_MIN", "30"))
    sched = BackgroundScheduler(timezone=os.getenv("TZ","America/Los_Angeles"))
    # 每 interval_min 分钟抓一轮 AB
    sched.add_job(refresh_ab_for_all, IntervalTrigger(minutes=interval_min), id="ab_refresh", replace_existing=True)
    return sched
