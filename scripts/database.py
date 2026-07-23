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

