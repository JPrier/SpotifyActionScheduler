import time
import schedule
from spotifyActionService.service.helper.actionHelper import parseActionFile, handleActions
from spotifyActionService.util.logger import logger
from spotifyActionService.util.env import get_env

# Setup Constants
INTERVAL = int(get_env("SYNC_INTERVAL_MINUTES", "60"))
SLEEP_TIME_IN_SECONDS = 5

def main():
    logger.info(f"Parsing action file...")
    actions = parseActionFile("spotifyActionService/actions.json")
    logger.info(f"Parsed {len(actions)} actions.")
    logger.info(f"Actions: {actions}")
    handleActions(actions)


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