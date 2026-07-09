import yfinance as yf
import sqlite3
import os
from datetime import datetime

# -----------------------------
# NVIDIA Stock Symbol
# -----------------------------
ticker = "NVDA"

# Fetch live stock data
stock = yf.Ticker(ticker)
info = stock.fast_info

# Current timestamp
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# -----------------------------
# Database Path
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(BASE_DIR, "data", "nvidia_stock.db")

# -----------------------------
# Connect to Database
# -----------------------------
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

# -----------------------------
# Store Data
# -----------------------------
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

# -----------------------------
# Display Data
# -----------------------------
print("\n===== NVIDIA LIVE STOCK DATA =====")

print("Timestamp       :", timestamp)
print("Ticker          :", ticker)
print("Current Price   :", info["lastPrice"])
print("Open Price      :", info["open"])
print("Previous Close  :", info["previousClose"])
print("Day High        :", info["dayHigh"])
print("Day Low         :", info["dayLow"])
print("Volume          :", info["lastVolume"])
print("Market Cap      :", info["marketCap"])
print("Currency        :", info["currency"])

print("\n✅ Data stored successfully in SQLite database.")