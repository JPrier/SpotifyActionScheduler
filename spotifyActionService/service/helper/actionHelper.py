import json
from spotifyActionService.models.actions import ActionType, Action, SyncAction, ArchiveAction, ACTION_MAP
from spotifyActionService.logic.playlistRefreshLogic import sync_playlists, archive_playlists

def parseActionFile(filepath: str) -> list[Action]:
    """
    Reads a JSON file with structure
      { "actions": [ { "type": "sync", "source": "...", ... }, ... ] }
    and returns a list of fully-typed Action instances.
    """
    with open(filepath, "r") as f:
        data = json.load(f)

    actions: list[Action] = []
    for raw in data.get("actions", []):
        # parse & validate the enum
        try:
            a_type = ActionType(raw["type"])
        except KeyError:
            raise KeyError(f"Missing 'type' in action: {raw!r}")
        except ValueError:
            raise ValueError(f"Unknown action type: {raw['type']}")

        cls = ACTION_MAP.get(a_type)
        if cls is None:
            raise RuntimeError(f"No class registered for action type {a_type}")

        # Build the dataclass—will TypeError if required fields are missing
        try:
            # strip out the raw['type'] since our constructor wants type=ActionType(...)
            params = {k: v for k, v in raw.items() if k != "type"}
            action_obj = cls(type=a_type, **params)
        except TypeError as e:
            raise ValueError(f"Invalid params for {a_type!r}: {e}")

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

def handleActions(actions: list[Action]) -> None:
    for action in actions:
        handleAction(action)

if __name__ == "__main__":
    # Example usage
    actions = parseActionFile("spotifyActionService/actions.json")
    handleActions(actions)
    