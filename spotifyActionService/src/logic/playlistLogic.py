from accessor.spotifyAccessor import SpotifyAccessor
from logic.mapper.spotifyMapper import map_to_id_set
from models.actions import ArchiveAction, SyncAction
from util.logger import logger


class PlaylistService:
    """
    Provides methods to manage playlists using a SpotifyAccessor.
    """
    def __init__(self, accessor: SpotifyAccessor):
        self.accessor = accessor

    def sync_playlists(self, action: SyncAction) -> None:
        """
        Synchronize the source playlist with the target playlist.
        Only adds tracks that are in the source but not in the target.
        """
        logger.info("Fetching source playlist items...")
        source_items = self.accessor.fetch_playlist_tracks(action.source_playlist_id)
        source_ids = map_to_id_set(source_items)

        logger.info("Fetching target playlist items...")
        target_items = self.accessor.fetch_playlist_tracks(action.target_playlist_id)
        target_ids = map_to_id_set(target_items)

        logger.info(f"Found {len(source_ids)} tracks in source playlist: {source_ids}")
        logger.info(f"Found {len(target_ids)} tracks in target playlist: {target_ids}")

        # Determine which source tracks aren't in the target
        tracks_to_add = [tid for tid in source_ids if tid not in target_ids]
        logger.info(f"Tracks to add: {tracks_to_add}")

        if not tracks_to_add:
            logger.info("No new tracks to add to target playlist.")
            return

        self.accessor.add_tracks_to_playlist(action.target_playlist_id, tracks_to_add)
        logger.info(
            f"Added {len(tracks_to_add)} tracks to target playlist: {action.target_playlist_id}"
        )

    def archive_playlists(self, action: ArchiveAction) -> None:
        """
        Archive the source playlist by copying its items to the target playlist.
        """
        logger.info("Fetching source playlist items...")
        source_items = self.accessor.fetch_playlist_tracks(action.source_playlist_id)
        source_ids = map_to_id_set(source_items)

        logger.info(f"Found {len(source_ids)} tracks in source playlist: {source_ids}")

        logger.info("Archiving source playlist...")
        target_playlist: str = action.target_playlist_id
        if not target_playlist:
            source_name: str = self.accessor.get_playlist_metadata(action.source_playlist_id)["name"]
            playlist = self.accessor.get_playlist_id_by_name(source_name)
        self.accessor.add_tracks_to_playlist(action.target_playlist_id, list(source_ids))
        logger.info(
            f"Archived {len(source_ids)} tracks to playlist: {action.target_playlist_id}"
        )

    def get_or_create_playlist_by_name(self, playlist_name: str) -> str:
        id = self.accessor.get_playlist_id_by_name(playlist_name)
        if not id:
            id = self.accessor.create_playlist_with_name(playlist_name)
        return id