from logic.playlistLogic import PlaylistService
from service.helper.actionHelper import ActionProcessor
from util.logger import logger


def main() -> None:
    logger.info("Starting on-demand handler...")

    logger.info("Parsing action file...")
    # Instantiate the processor with a real PlaylistService
    processor = ActionProcessor(playlist_service=PlaylistService())
    actions = processor.parse_action_file("spotifyActionService/actions.json")
    logger.info(f"Parsed {len(actions)} actions.")
    logger.info(f"Actions: {actions}")

    logger.info("Handling actions...")
    processor.handle_actions(actions)


if __name__ == "__main__":  # pragma: no cover
    main()
