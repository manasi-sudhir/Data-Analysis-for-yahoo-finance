import logging
import os
from datetime import datetime, timedelta

from scripts.config import DAILY_HISTORY_REFRESH_HOURS, LOG_DIR
from scripts import database
from scripts.fetch_data import fetch_live_snapshot, fetch_daily_history
from scripts.data_cleaning import clean_intraday, clean_daily
from scripts.feature_engineering import add_intraday_features, add_daily_features

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


def run_pipeline(force_daily_refresh: bool = False):
    global _last_daily_refresh
    database.init_db()

    # 1. Live snapshot - fast, cheap, do it every pass
    try:
        snapshot = fetch_live_snapshot()
        if snapshot["current_price"] is None:
            logger.warning("Live snapshot came back with no price - market may be closed. Skipping insert.")
        else:
            database.insert_live_snapshot(snapshot)
            logger.info(f"Inserted live snapshot @ {snapshot['timestamp']} price={snapshot['current_price']}")
    except Exception as e:
        logger.error(f"Live snapshot fetch failed: {e}")

    # 2. Daily history - heavier, only refresh periodically
    if force_daily_refresh or _should_refresh_daily_history():
        try:
            daily_raw = fetch_daily_history()
            database.upsert_daily_history(daily_raw)
            _last_daily_refresh = datetime.now()
            logger.info(f"Refreshed daily history: {len(daily_raw)} rows")
        except Exception as e:
            logger.error(f"Daily history fetch failed: {e}")

    # 3 & 4. Clean + engineer features from whatever raw data now exists
    try:
        raw_intraday = database.read_table("nvidia_stock_data")
        cleaned_intraday = clean_intraday(raw_intraday)
        featured_intraday = add_intraday_features(cleaned_intraday)
        database.replace_table(featured_intraday, "nvidia_intraday_features")

        raw_daily = database.read_table("nvidia_daily_history")
        cleaned_daily = clean_daily(raw_daily)
        featured_daily = add_daily_features(cleaned_daily)
        database.replace_table(featured_daily, "nvidia_daily_features")

        logger.info(
            f"Feature tables rebuilt: intraday={len(featured_intraday)} rows, "
            f"daily={len(featured_daily)} rows"
        )
    except Exception as e:
        logger.error(f"Cleaning/feature engineering step failed: {e}")


if __name__ == "__main__":
    run_pipeline(force_daily_refresh=True)