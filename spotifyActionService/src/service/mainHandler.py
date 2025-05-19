import dependency.spotifyClient as _spotifyClient
import logic.playlistLogic as _pl_logic
import service.onDemandHandler as _odh
import service.schedulerHandler as _sch
from accessor.spotifyAccessor import SpotifyAccessor as _SpotifyAccessor
from models.actions import ActionType, ArchiveAction, SyncAction


def do_sync(
    source_playlist_id: str,
    target_playlist_id: str,
    avoid_duplicates: bool = True,
) -> None:
    """
    Sync one playlist into another.
    """
    client = _spotifyClient.get_client()
    accessor = _SpotifyAccessor(client)
    service = _pl_logic.PlaylistService(accessor)
    action = SyncAction(
        type=ActionType.SYNC,
        source_playlist_id=source_playlist_id,
        target_playlist_id=target_playlist_id,
        avoid_duplicates=avoid_duplicates,
    )
    service.sync_playlists(action)
    print(f"✅ Synced from {source_playlist_id!r} → {target_playlist_id!r}")


def do_archive(
    source_playlist_id: str,
    target_playlist_id: str | None = None,
    days: int = 30,
    avoid_duplicates: bool = True,
    filter_by_time: bool = True,
) -> None:
    """
    Archive tracks from a source playlist into a target (or remove if target is None).
    Only tracks older than `days` days will be archived if filter_by_time is True.
    """
    client = _spotifyClient.get_client()
    accessor = _SpotifyAccessor(client)
    service = _pl_logic.PlaylistService(accessor)
    action = ArchiveAction(
        type=ActionType.ARCHIVE,
        timeBetweenActInSeconds=days * 24 * 3600,
        source_playlist_id=source_playlist_id,
        target_playlist_id=target_playlist_id,
        avoid_duplicates=avoid_duplicates,
        filter_by_time=filter_by_time,
    )
    service.archive_playlists(action)
    tgt = target_playlist_id or "removed"
    print(f"✅ Archived from {source_playlist_id!r} → {tgt!r}")


def run_actions_once() -> None:
    """
    Process all queued actions one time (on-demand).
    """
    _odh.main()


def start_scheduled_actions() -> None:
    """
    Start the scheduler (this will block and run your recurring jobs).
    """
    _sch.main()
