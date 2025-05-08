import time

import schedule
from logic.playlistLogic import PlaylistService
from models.actions import Action
from service.helper.actionHelper import ActionProcessor
from util.logger import logger

# Setup Constants
SLEEP_TIME_IN_SECONDS = 1


def schedule_action(processor: ActionProcessor, action: Action) -> None:
    """
    Schedule the action to run at the specified time.
    """
    logger.info(f"Scheduling action: {action}")
    schedule.every(action.timeBetweenActInSeconds).seconds.do(
        processor.handleAction, action
    )


def main() -> None:
    processor = ActionProcessor(playlist_service=PlaylistService())
    actions = processor.parse_action_file("spotifyActionService/actions.json")

    # Setup Schedule
    for action in actions:
        schedule_action(processor, action)

    # Start Schedule
    while True:
        schedule.run_pending()
        time.sleep(SLEEP_TIME_IN_SECONDS)


if __name__ == "__main__":  # pragma: no cover
    main()
