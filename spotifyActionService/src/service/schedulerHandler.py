import time

import schedule
from models.actions import Action
from service.helper.actionHelper import (
    handleAction,
    parseActionFile,
)
from util.logger import logger

# Setup Constants
SLEEP_TIME_IN_SECONDS = 1


def get_actions() -> list[Action]:
    """
    Fetch actions from the action file.
    """
    logger.info("Parsing action file...")
    actions = parseActionFile("spotifyActionService/actions.json")
    logger.info(f"Parsed {len(actions)} actions: {actions}")
    return actions


def schedule_action(action: Action) -> None:
    """
    Schedule the action to run at the specified time.
    """
    logger.info(f"Scheduling action: {action}")
    schedule.every(action.timeBetweenActInSeconds).seconds.do(handleAction, action)


def main() -> None:
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
