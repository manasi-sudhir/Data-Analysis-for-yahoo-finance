import sqlite3
import pandas as pd

# Connect to database
connection = sqlite3.connect("data/nvidia_stock.db")

# Read the table into a DataFrame
df = pd.read_sql_query("SELECT * FROM nvidia_stock_data", connection)

# Show all columns
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

print(df)

connection.close()