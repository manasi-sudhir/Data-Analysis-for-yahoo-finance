import logging
import time
from datetime import datetime, timedelta

from src.config import DAILY_HISTORY_REFRESH_HOURS, LOG_DIR
from src import database
from src.fetch_data import fetch_live_snapshot, fetch_daily_history
from src.data_cleaning import clean_intraday, clean_daily
from src.feature_engineering import add_intraday_features, add_daily_features

import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "pipeline.log")),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("nvidia_pipeline")

_last_daily_refresh = None


def _should_refresh_daily_history() -> bool:
    global _last_daily_refresh
    if _last_daily_refresh is None:
        return True
    return datetime.now() - _last_daily_refresh > timedelta(hours=DAILY_HISTORY_REFRESH_HOURS)

