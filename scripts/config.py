import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_DIR = os.path.join(BASE_DIR, "logs")
DB_PATH = os.path.join(DATA_DIR, "nvidia_stock.db")

TICKER = "NVDA"

LIVE_FETCH_INTERVAL_SECONDS = 60
DAILY_HISTORY_REFRESH_HOURS = 6
DAILY_HISTORY_PERIOD = "2y"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
