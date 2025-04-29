import time
import schedule
from logic.playlistRefreshLogic import sync_playlists
from util.logger import logger
from util.env import get_env

# Setup Constants
INTERVAL = int(get_env("SYNC_INTERVAL_MINUTES", "60"))
SLEEP_TIME_IN_SECONDS = 5

def main():
    sync_playlists()


if __name__ == "__main__":
    # Setup Schedule
    logger.info(f"Scheduling sync every {INTERVAL} minute(s)")
    schedule.every(INTERVAL).minutes.do(main)

    # Run once on startup
    main()

    # Start Schedule
    while True:
        schedule.run_pending()
        time.sleep(SLEEP_TIME_IN_SECONDS)