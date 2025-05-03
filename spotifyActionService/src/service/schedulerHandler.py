import time
import schedule
from service.helper.actionHelper import (
    parseActionFile,
    handleAction,
)
from util.logger import logger
from models.actions import Action

# Setup Constants
SLEEP_TIME_IN_SECONDS = 1


def get_actions():
    """
    Fetch actions from the action file.
    """
    logger.info("Parsing action file...")
    actions = parseActionFile("spotifyActionService/actions.json")
    logger.info(f"Parsed {len(actions)} actions: {actions}")
    return actions


def schedule_action(action: Action):
    """
    Schedule the action to run at the specified time.
    """
    logger.info(f"Scheduling action: {action}")
    schedule.every(action.timeBetweenActInSeconds).seconds.do(handleAction, action)


def main():
    actions = get_actions()

    # Setup Schedule
    for action in actions:
        schedule_action(action)

    # Start Schedule
    while True:
        schedule.run_pending()
        time.sleep(SLEEP_TIME_IN_SECONDS)


if __name__ == "__main__":
    main()
