from dataclasses import dataclass
from enum import StrEnum


class ActionType(StrEnum):
    SYNC = "sync"
    ARCHIVE = "archive"


@dataclass(kw_only=True)
class Action:
    """Base class for all actions."""

    type: ActionType
    timeBetweenActInSeconds: int = 30  # Default to 30 seconds


@dataclass
class SyncAction(Action):
    source_playlist_id: str
    target_playlist_id: str
    avoid_duplicates: bool = True


@dataclass
class ArchiveAction(Action):
    source_playlist_id: str
    target_playlist_id: str | None
    avoid_duplicates: bool = True
    filter_by_time: bool = True


# Map each enum to its dataclass
ACTION_MAP: dict[ActionType, type[Action]] = {
    ActionType.SYNC: SyncAction,
    ActionType.ARCHIVE: ArchiveAction,
}
