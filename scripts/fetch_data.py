"""
Everything that talks to Yahoo Finance lives here. Two kinds of fetch:

  fetch_live_snapshot()   -> one row "right now" snapshot (price/volume/etc)
                              cheap call, safe to poll every ~minute
  fetch_daily_history()   -> full daily OHLCV bars over DAILY_HISTORY_PERIOD
                              heavier call, only needs refreshing a few times a day
"""
import logging
from datetime import datetime

import pandas as pd
import yfinance as yf

from src.config import TICKER, DAILY_HISTORY_PERIOD

logger = logging.getLogger("nvidia_pipeline.fetch")

def fetch_live_snapshot() -> dict:
    """Pulls a single current snapshot via yfinance's fast_info."""
    stock = yf.Ticker(TICKER)
    info = stock.fast_info

    row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ticker": TICKER,
        "current_price": info.get("lastPrice"),
        "open_price": info.get("open"),
        "previous_close": info.get("previousClose"),
        "day_high": info.get("dayHigh"),
        "day_low": info.get("dayLow"),
        "volume": info.get("lastVolume"),
        "market_cap": info.get("marketCap"),
        "currency": info.get("currency"),
    }
    return row

def fetch_daily_history(period: str = DAILY_HISTORY_PERIOD) -> pd.DataFrame:
    """Pulls daily OHLCV bars. Returned columns match nvidia_daily_history schema."""
    stock = yf.Ticker(TICKER)
    hist = stock.history(period=period, interval="1d")

    if hist.empty:
        logger.warning("yfinance returned no daily history data")
        return pd.DataFrame(columns=["date", "ticker", "open", "high", "low", "close", "volume"])

    hist = hist.reset_index()
    hist["date"] = hist["Date"].dt.strftime("%Y-%m-%d")
    hist["ticker"] = TICKER
    hist = hist.rename(columns={
        "Open": "open", "High": "high", "Low": "low",
        "Close": "close", "Volume": "volume"
    })
    return hist[["date", "ticker", "open", "high", "low", "close", "volume"]]


if __name__ == "__main__":
    print(fetch_live_snapshot())
    print(fetch_daily_history().tail())
