import sqlite3
import os

# Get project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database path
db_path = os.path.join(BASE_DIR, "data", "nvidia_stock.db")

# Connect to SQLite database
connection = sqlite3.connect(db_path)

cursor = connection.cursor()

# Create table
cursor.execute("""
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

connection.commit()
connection.close()

print("Database and table created successfully!")