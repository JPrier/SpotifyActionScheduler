from accessor.configLoader import load_json_file
from logic.playlistLogic import PlaylistService
from models.actions import ACTION_MAP, Action, ActionType
from util.logger import logger


class ActionProcessor:
    """
    Encapsulates parsing and handling of action definitions.
    """

    def __init__(self, playlist_service: PlaylistService) -> None:
        self.playlist_service = playlist_service

    def parse_action_file(self, filepath: str) -> list[Action]:
        """
        Reads a JSON file and returns a list of Action instances.
        """
        data: dict = load_json_file(filepath)
        actions: list[Action] = []

        for raw in data.get("actions", []):
            # parse & validate the enum
            try:
                a_type = ActionType(raw["type"])
            except KeyError as err:
                raise KeyError(f"Missing 'type' in action: {raw!r}") from err
            except ValueError as err:
                raise ValueError(f"Unknown action type: {raw['type']}") from err

            cls = ACTION_MAP.get(a_type)
            if cls is None:
                raise RuntimeError(f"No class registered for action type {a_type}")

            # Build the dataclass—will TypeError if required fields are missing
            try:
                params = {k: v for k, v in raw.items() if k != "type"}
                action_obj = cls(type=a_type, **params)
            except TypeError as err:
                raise ValueError(f"Invalid params for {a_type!r}: {err}") from err

            actions.append(action_obj)

        return actions

    def handle_action(self, action: Action) -> None:
        """
        Dispatches a single Action to the appropriate PlaylistService method.
        """
        match action.type:
            case ActionType.SYNC:
                self.playlist_service.sync_playlists(action)
            case ActionType.ARCHIVE:
                self.playlist_service.archive_playlists(action)
            case _:
                logger.warning(f"Unhandled action type: {action.type}")

    def handle_actions(self, actions: list[Action]) -> None:
        """
        Processes a list of Actions in sequence.
        """
        for action in actions:
            self.handle_action(action)
