from datetime import UTC, datetime, timedelta

from accessor.spotifyAccessor import SpotifyAccessor
from logic.mapper.spotifyMapper import map_to_id_set
from models.actions import ArchiveAction, SyncAction
from util.logger import logger


class PlaylistService:
    """
    Provides methods to manage playlists using a SpotifyAccessor.
    """

    def __init__(self, accessor: SpotifyAccessor) -> None:
        self.accessor = accessor

    def filter_items_after_time(self, items: list[str], time_in_seconds: int) -> list:
        """
        Filters items based on a time threshold.
        Returns items that were added after the specified time.
        """
        cutoff = datetime.now(UTC) - timedelta(seconds=time_in_seconds)
        logger.info(
            "Filtering tracks added after %s (last %s seconds)",
            cutoff.isoformat(),
            time_in_seconds,
        )

        filtered_items = [
            item
            for item in items
            if datetime.fromisoformat(item["added_at"].replace("Z", "+00:00")) > cutoff
        ]
        logger.info("Filtered items: %s", filtered_items)
        return filtered_items

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

        logger.info(
            "Found %s tracks in source playlist: %s", len(source_ids), source_ids
        )
        logger.info(
            "Found %s tracks in target playlist: %s", len(target_ids), target_ids
        )

        # Determine which source tracks aren't in the target
        tracks_to_add = [tid for tid in source_ids if tid not in target_ids]
        logger.info("Tracks to add: %s", tracks_to_add)

        if not tracks_to_add:
            logger.info("No new tracks to add to target playlist.")
            return

        self.accessor.add_tracks_to_playlist(action.target_playlist_id, tracks_to_add)
        logger.info(
            "Added %s tracks to target playlist: %s",
            len(tracks_to_add),
            action.target_playlist_id,
        )

    def archive_playlists(self, action: ArchiveAction) -> None:
        """
        Archive the source playlist by copying new items into '{source_name}-Archive'.
        Creates the archive playlist if it does not exist.
        Optionally avoids duplicates.
        """
        logger.info("Fetching source playlist items...")
        source_items = self.accessor.fetch_playlist_tracks(action.source_playlist_id)

        if getattr(action, "filter_by_time", True):
            logger.info("Filtering source playlist items by time...")
            source_items = self.filter_items_after_time(
                source_items, action.timeBetweenActInSeconds
            )

        source_ids = map_to_id_set(source_items)
        logger.info(
            "Found %s tracks in source playlist: %s", len(source_ids), source_ids
        )

        # Determine archive playlist name and ensure it exists
        source_name = self.accessor.get_playlist_metadata(action.source_playlist_id)[
            "name"
        ]
        archive_name = f"{source_name}-Archive"
        logger.info("Using archive playlist name: '%s'", archive_name)
        archive_playlist_id = self.accessor.get_or_create_playlist_with_name(
            archive_name
        )

        # Determine which tracks to add
        if getattr(action, "avoidDuplicates", False):
            logger.info(
                "Avoiding duplicates: fetching existing archive playlist items..."
            )
            existing_items = self.accessor.fetch_playlist_tracks(archive_playlist_id)
            existing_ids = map_to_id_set(existing_items)
            tracks_to_add = [tid for tid in source_ids if tid not in existing_ids]
            logger.info("Tracks to add after duplicate check: %s", tracks_to_add)
        else:
            tracks_to_add = list(source_ids)
            logger.info("Adding all tracks without duplicate check: %s", tracks_to_add)

        if not tracks_to_add:
            logger.info("No new tracks to archive.")
            return

        # Add tracks to archive playlist
        self.accessor.add_tracks_to_playlist(archive_playlist_id, tracks_to_add)
        logger.info(
            "Archived %s tracks to playlist '%s' (ID: %s)",
            len(tracks_to_add),
            archive_name,
            archive_playlist_id,
        )
