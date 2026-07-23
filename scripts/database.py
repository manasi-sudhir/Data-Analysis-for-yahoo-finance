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


    # Processed / feature-engineered daily table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS nvidia_daily_features (
        date TEXT PRIMARY KEY,
        ticker TEXT,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume INTEGER,
        daily_return REAL,
        log_return REAL,
        sma_20 REAL,
        sma_50 REAL,
        ema_12 REAL,
        ema_26 REAL,
        macd REAL,
        macd_signal REAL,
        macd_hist REAL,
        rsi_14 REAL,
        bb_mid REAL,
        bb_upper REAL,
        bb_lower REAL,
        volatility_20 REAL,
        volume_change_pct REAL,
        momentum_10 REAL
    )
    """)

    conn.commit()
    conn.close()


def read_table(table_name: str) -> pd.DataFrame:
    conn = get_connection()
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    except pd.errors.DatabaseError:
        df = pd.DataFrame()
    conn.close()
    return df

def read_table(table_name: str) -> pd.DataFrame:
    conn = get_connection()
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    except pd.errors.DatabaseError:
        df = pd.DataFrame()
    conn.close()
    return df


def upsert_daily_history(df: pd.DataFrame):
    """Replace rows by date (primary key) so re-running is idempotent."""
    if df.empty:
        return
    conn = get_connection()
    cur = conn.cursor()
    rows = df[["date", "ticker", "open", "high", "low", "close", "volume"]].values.tolist()
    cur.executemany("""
        INSERT INTO nvidia_daily_history (date, ticker, open, high, low, close, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET
            open=excluded.open, high=excluded.high, low=excluded.low,
            close=excluded.close, volume=excluded.volume, ticker=excluded.ticker
    """, rows)
    conn.commit()
    conn.close()


def replace_table(df: pd.DataFrame, table_name: str):
    """Used for processed feature tables - simplest to fully rebuild each run
    since they're derived data, not a growing log."""
    conn = get_connection()
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()

def insert_live_snapshot(row: dict):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO nvidia_stock_data (
            timestamp, ticker, current_price, open_price, previous_close,
            day_high, day_low, volume, market_cap, currency
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        row["timestamp"], row["ticker"], row["current_price"], row["open_price"],
        row["previous_close"], row["day_high"], row["day_low"], row["volume"],
        row["market_cap"], row["currency"]
    ))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print(f"Database ready at {DB_PATH}")

