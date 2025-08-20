import re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; WatchABBot/1.0; +https://example.com/bot)"
}

BASE = "https://www.americanbulls.com/SignalPage.aspx?lang=en&Ticker={symbol}"

def parse_signal_history(soup):
    """
    从 'Signal History' 表格里抓最新两条（日期+信号类型）。
    页面示例可见：存在“Signal History”表格，列出 Date/Price/Signal 等。"""
    history = []
    # 找到包含 "Signal History" 的标题，再找后面的表格
    header = soup.find(string=re.compile(r"Signal History", re.I))
    if not header:
        return history
    table = header.find_parent().find_next("table")
    if not table:
        return history
    # 跳过表头，抓前2行
    rows = table.find_all("tr")
    for tr in rows[1:3]:
        tds = [td.get_text(strip=True) for td in tr.find_all("td")]
        if len(tds) >= 3:
            date = tds[0]
            signal = tds[2].upper()
            history.append({"date": date, "signal": signal})
    return history

def parse_suggestion_and_update(soup):
    """
    抓页面冒头的大字建议（如 STAY LONG / BUY 等）以及 'Signal Update' 一段话。
    页面示例可见：大标题区域有建议词；下方存在 'Signal Update' 段落文本。"""
    # 顶部建议：找像 'STAY LONG' 这类词
    suggest = None
    for tag in soup.find_all(text=True):
        txt = tag.strip().upper()
        if txt in {"BUY", "SELL", "SHORT", "STAY LONG"}:
            suggest = txt
            break

    # Signal Update 段落
    summary = None
    su = soup.find(string=re.compile(r"Signal Update", re.I))
    if su:
        # 通常 'Signal Update' 下一个 block 就是文本
        p = su.find_parent().find_next(["p","div"])
        if p:
            summary = p.get_text(" ", strip=True)
    return suggest, summary

def fetch_ab_for_symbol(symbol: str):
    url = BASE.format(symbol=symbol.upper())
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    suggestion, summary = parse_suggestion_and_update(soup)
    last_two = parse_signal_history(soup)
    return {
        "symbol": symbol.upper(),
        "suggestion": suggestion,
        "summary": summary,
        "last_two_actions": last_two,
    }
