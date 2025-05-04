from service.helper.actionHelper import (
    handleActions,
    parseActionFile,
)
from util.logger import logger


def main() -> None:
    logger.info("Starting on-demand handler...")

    logger.info("Parsing action file...")
    actions = parseActionFile("spotifyActionService/actions.json")
    logger.info(f"Parsed {len(actions)} actions.")
    logger.info(f"Actions: {actions}")
    handleActions(actions)


if __name__ == "__main__":  # pragma: no cover
    main()
