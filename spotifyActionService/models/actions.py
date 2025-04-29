from enum import StrEnum
from dataclasses import dataclass
from typing import Type

class ActionType(StrEnum):
    SYNC = "sync"
    ARCHIVE = "archive"

@dataclass
class Action:
    """Base class for all actions."""
    type: ActionType

@dataclass
class SyncAction(Action):
    source_playlist_id: str
    target_playlist_id: str
    avoid_duplicates: bool = True

@dataclass
class ArchiveAction(Action):
    source_playlist_id: str
    target_playlist_id: str
    avoid_duplicates: bool = True

# Map each enum to its dataclass
ACTION_MAP: dict[ActionType, Type[Action]] = {
    ActionType.SYNC:   SyncAction,
    ActionType.ARCHIVE: ArchiveAction,
}