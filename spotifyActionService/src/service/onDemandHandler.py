from spotifyActionService.src.service.helper.actionHelper import (
    parseActionFile,
    handleActions,
)
from spotifyActionService.src.util.logger import logger


def main():
    logger.info("Starting on-demand handler...")

    logger.info("Parsing action file...")
    actions = parseActionFile("spotifyActionService/actions.json")
    logger.info(f"Parsed {len(actions)} actions.")
    logger.info(f"Actions: {actions}")
    handleActions(actions)


if __name__ == "__main__":
    main()
