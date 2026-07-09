import yfinance as yf
from datetime import datetime
ticker = "NVDA"
stock = yf.Ticker(ticker)
info = stock.fast_info
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print("Timestamp:", timestamp)
print("Ticker:", ticker)
print("Current Price:", info["lastPrice"])
print("Open Price:", info["open"])
print("Previous Close:", info["previousClose"])
print("Day High:", info["dayHigh"])
print("Day Low:", info["dayLow"])
print("Volume:", info["lastVolume"])
print("Market Cap:", info["marketCap"])
print("Currency:", info["currency"])