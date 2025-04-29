from spotifyActionService.util.logger import logger
from spotifyActionService.accessor.spotifyAccessor import fetch_playlist_tracks, add_tracks_to_playlist, get_metadata
from spotifyActionService.logic.mapper.spotifyMapper import map_to_id_set
from spotifyActionService.models.actions import ActionType, Action, SyncAction, ArchiveAction

# def collect_duplicates(playlist_items: list) -> dict[str, list[int]]:
#     """
#     Collect duplicates from the playlist items.
#     Returns a dictionary where the keys are track IDs and the values are lists of positions of duplicates.
#     """
#     # Create a dictionary to store the occurrences of each track ID
#     # Occurences -> {track_id: [{position: ..., added_at: ...}, ...]}
#     occurrences: dict[str, list[dict]] = {}
#     for index, item in enumerate(playlist_items):
#         track_id = item["track"]["id"]
#         occurrences.setdefault(track_id, []).append({
#                 "position": index,
#                 "added_at": item["added_at"]
#             })
        
#     # Collect dictionary of duplicates
#     # duplicates = {track_id: [position1, position2, ...]}
#     duplicates: dict[str, list[int]] = {}
#     for track_id, items in occurrences.items():
#         # If there are no duplicates, skip
#         if len(items) <= 1:
#             continue
#         # Sort by 'added_at', remove the oldest from the list and keep the rest
#         to_remove = sorted(items, key=lambda o: o["added_at"])[1:]
#         duplicates[track_id] = [item["position"] for item in to_remove]

#     return duplicates


def sync_playlists(action: SyncAction) -> None:
    """
    Synchronize the source playlist with the target playlist by copying items from the source to the target.    
    """
    logger.info("Fetching source playlist items...")
    source_items = fetch_playlist_tracks(action.source_playlist_id)
    source_ids = map_to_id_set(source_items)

    logger.info("Fetching target playlist items...")
    target_items = fetch_playlist_tracks(action.target_playlist_id)
    target_ids = map_to_id_set(target_items)

    # if len(target_ids) < len(target_items) and action.avoid_duplicates:
    #     logger.warning("Target playlist has duplicates removing duplicates...")
    #     duplicates = collect_duplicates(target_items)
    #     if duplicates:
    #         remove_tracks_from_playlist(action.target_playlist_id, snapshot_id, duplicates)
            
    logger.info(f"Found {len(source_ids)} tracks in source playlist: {source_ids}")
    logger.info(f"Found {len(target_ids)} tracks in target playlist: {target_ids}")

    # Find which source tracks aren’t yet in the target
    tracks_to_add = [track_id for track_id in source_ids if track_id not in target_ids]
    logger.info(f"Tracks to add: {tracks_to_add}")

    add_tracks_to_playlist(action.target_playlist_id, tracks_to_add)
    logger.info(f"Added {len(tracks_to_add)} tracks to target playlist: {action.target_playlist_id}")


def archive_playlists(action: ArchiveAction) -> None:
    """
    Archive the source playlist by copying its items to the target playlist.
    """
    logger.info("Fetching source playlist items...")
    source_items = fetch_playlist_tracks(action.source_playlist_id)
    source_ids = map_to_id_set(source_items)

    logger.info(f"Found {len(source_ids)} tracks in source playlist: {source_ids}")

    logger.info("Archiving source playlist...")