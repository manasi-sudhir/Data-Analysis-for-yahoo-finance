import time
import logging

from scripts.config import LIVE_FETCH_INTERVAL_SECONDS
from scripts.pipeline import run_pipeline

logger = logging.getLogger("nvidia_pipeline.scheduler")


def main():
    logger.info(f"Starting scheduler, polling every {LIVE_FETCH_INTERVAL_SECONDS}s. Ctrl+C to stop.")
    # Do one full pass immediately (including daily history) so the DB isn't empty on first run
    run_pipeline(force_daily_refresh=True)

    while True:
        try:
            time.sleep(LIVE_FETCH_INTERVAL_SECONDS)
            run_pipeline()
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user.")
            break
        except Exception as e:
            logger.error(f"Unexpected error in scheduler loop: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
