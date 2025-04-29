from spotifyActionService.util.logger import logger
from spotifyActionService.accessor.spotifyAccessor import fetch_playlist_tracks, convert_playlist_to_ordered_id_list
from spotifyActionService.models.actions import ActionType, Action, SyncAction, ArchiveAction

def sync_playlists(action: SyncAction) -> None:
    """
    Synchronize the source playlist with the target playlist by copying items from the source to the target.    
    """
    logger.info("Fetching target playlist items...")
    target_items = fetch_playlist_tracks(action.target_playlist_id)
    target_ids = convert_playlist_to_ordered_id_list(target_items)

    logger.info("Fetching source playlist items...")
    source_items = fetch_playlist_tracks(action.source_playlist_id)
    source_ids = convert_playlist_to_ordered_id_list(source_items)

    logger.info(f"Found {len(source_ids)} tracks in source playlist (oldest→newest): {source_ids}")
    logger.info(f"Found {len(target_ids)} tracks in target playlist (oldest→newest): {target_ids}")

def archive_playlists(action: ArchiveAction) -> None:
    """
    Archive the source playlist by copying its items to the target playlist.
    """
    logger.info("Fetching source playlist items...")
    source_items = fetch_playlist_tracks(action.source_playlist_id)
    source_ids = convert_playlist_to_ordered_id_list(source_items)

    logger.info(f"Found {len(source_ids)} tracks in source playlist (oldest→newest): {source_ids}")

    logger.info("Archiving source playlist...")

if __name__ == "__main__":
    sync_playlists()