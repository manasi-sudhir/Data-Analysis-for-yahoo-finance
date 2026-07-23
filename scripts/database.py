import sqlite3
import pandas as pd
from src.config import DB_PATH


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Raw live snapshot table (kept identical to the original script's schema)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS nvidia_stock_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        ticker TEXT,
        current_price REAL,
        open_price REAL,
        previous_close REAL,
        day_high REAL,
        day_low REAL,
        volume INTEGER,
        market_cap REAL,
        currency TEXT
    )
    """)
# Raw daily OHLCV history
    cur.execute("""
    CREATE TABLE IF NOT EXISTS nvidia_daily_history (
        date TEXT PRIMARY KEY,
        ticker TEXT,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume INTEGER
    )
    """)

    # Processed / feature-engineered intraday table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS nvidia_intraday_features (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT UNIQUE,
        ticker TEXT,
        current_price REAL,
        open_price REAL,
        previous_close REAL,
        day_high REAL,
        day_low REAL,
        volume INTEGER,
        market_cap REAL,
        currency TEXT,
        price_change REAL,
        pct_change_from_prev_snapshot REAL,
        pct_change_from_open REAL,
        rolling_mean_10 REAL,
        rolling_std_10 REAL,
        rolling_mean_30 REAL,
        day_range_pct REAL,
        volume_zscore REAL
    )
    """)

