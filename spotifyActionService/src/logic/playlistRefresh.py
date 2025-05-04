from accessor.spotifyAccessor import (
    add_tracks_to_playlist,
    fetch_playlist_tracks,
)
from logic.mapper.spotifyMapper import map_to_id_set
from models.actions import ArchiveAction, SyncAction
from util.logger import logger


def sync_playlists(action: SyncAction) -> None:
    """
    Synchronize the source playlist with the target playlist.
    This will only add tracks that are in the source but not in the target.
    """
    logger.info("Fetching source playlist items...")
    source_items = fetch_playlist_tracks(action.source_playlist_id)
    source_ids = map_to_id_set(source_items)

    logger.info("Fetching target playlist items...")
    target_items = fetch_playlist_tracks(action.target_playlist_id)
    target_ids = map_to_id_set(target_items)

    logger.info(f"Found {len(source_ids)} tracks in source playlist: {source_ids}")
    logger.info(f"Found {len(target_ids)} tracks in target playlist: {target_ids}")

    # Find which source tracks aren’t yet in the target
    tracks_to_add = [track_id for track_id in source_ids if track_id not in target_ids]
    logger.info(f"Tracks to add: {tracks_to_add}")

    if not tracks_to_add:
        logger.info("No new tracks to add to target playlist.")
        return

    add_tracks_to_playlist(action.target_playlist_id, tracks_to_add)
    logger.info(
        f"Added {len(tracks_to_add)} tracks to "
        + f"target playlist: {action.target_playlist_id}"
    )


def archive_playlists(action: ArchiveAction) -> None:
    """
    Archive the source playlist by copying its items to the target playlist.
    """
    logger.info("Fetching source playlist items...")
    source_items = fetch_playlist_tracks(action.source_playlist_id)
    source_ids = map_to_id_set(source_items)

    logger.info(f"Found {len(source_ids)} tracks in source playlist: {source_ids}")

    logger.info("Archiving source playlist...")
