from util.env import get_environ
from util.logger import logger
from accessor.spotifyAccessor import fetch_playlist_tracks, convert_playlist_to_ordered_id_list

def sync_playlists():
    """
    Main entrypoint: fetch source & target playlists, convert to ordered ID lists, and log them.
    """
    source_id = get_environ("SOURCE_PLAYLIST_ID")
    target_id = get_environ("TARGET_PLAYLIST_ID")

    logger.info("Fetching target playlist items...")
    target_items = fetch_playlist_tracks(target_id)
    target_ids = convert_playlist_to_ordered_id_list(target_items)

    logger.info("Fetching source playlist items...")
    source_items = fetch_playlist_tracks(source_id)
    source_ids = convert_playlist_to_ordered_id_list(source_items)

    logger.info(f"Found {len(source_ids)} tracks in source playlist (oldest→newest): {source_ids}")
    logger.info(f"Found {len(target_ids)} tracks in target playlist (oldest→newest): {target_ids}")


if __name__ == "__main__":
    sync_playlists()