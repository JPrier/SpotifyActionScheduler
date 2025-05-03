from accessor.configLoader import load_json_file
from models.actions import ActionType, Action, ACTION_MAP
from logic.playlistRefreshLogic import (
    sync_playlists,
    archive_playlists,
)
from typing import Dict, List


def parseActionFile(filepath: str) -> List[Action]:
    """
    Reads a JSON file with structure
      { "actions": [ { "type": "sync", "source": "...", ... }, ... ] }
    and returns a list of fully-typed Action instances.
    """
    data: Dict = load_json_file(filepath)

    actions: List[Action] = []
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
            # strip out the raw['type'] since our constructor wants type=ActionType(...)
            params = {k: v for k, v in raw.items() if k != "type"}
            action_obj = cls(type=a_type, **params)
        except TypeError as err:
            raise ValueError(f"Invalid params for {a_type!r}: {err}") from err

        actions.append(action_obj)

    return actions


def handleAction(action: Action) -> None:
    match action.type:
        case ActionType.SYNC:
            sync_playlists(action)
        case ActionType.ARCHIVE:
            archive_playlists(action)
        case _:
            pass


def handleActions(actions: List[Action]) -> None:
    for action in actions:
        handleAction(action)


if __name__ == "__main__":
    # Example usage
    actions = parseActionFile("spotifyActionService/actions.json")
    handleActions(actions)
