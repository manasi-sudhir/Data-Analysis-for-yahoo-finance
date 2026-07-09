import sqlite3
import os

# Get project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database path
db_path = os.path.join(BASE_DIR, "data", "nvidia_stock.db")

# Connect to database
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

# Fetch all records
cursor.execute("SELECT * FROM nvidia_stock_data")

rows = cursor.fetchall()

print("\n===== NVIDIA STOCK DATABASE =====\n")

for row in rows:
    print(row)

connection.close()