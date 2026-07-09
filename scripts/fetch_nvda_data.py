import yfinance as yf
from datetime import datetime
import sqlite3
import os
ticker = "NVDA"
stock = yf.Ticker(ticker)
info = stock.fast_info
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# Get project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database path
db_path = os.path.join(BASE_DIR, "data", "nvidia_stock.db")

# Connect to SQLite database
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

# Insert live stock data
cursor.execute("""
INSERT INTO nvidia_stock_data (
    timestamp,
    ticker,
    current_price,
    open_price,
    previous_close,
    day_high,
    day_low,
    volume,
    market_cap,
    currency
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    timestamp,
    ticker,
    info["lastPrice"],
    info["open"],
    info["previousClose"],
    info["dayHigh"],
    info["dayLow"],
    info["lastVolume"],
    info["marketCap"],
    info["currency"]
))

connection.commit()
connection.close()

print("✅ Live NVIDIA stock data stored successfully!")
print("Timestamp:", timestamp)
print("Current Price:", info["lastPrice"])