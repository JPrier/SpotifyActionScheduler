from typing import Any, List, Dict, Optional

from dependency.spotifyClient import spotify_client
from util.logger import logger

class SpotifyAccessor:
    """
    Encapsulates a Spotipy client and current user ID, and provides
    helper methods for common playlist operations.
    """
    def __init__(
        self,
        client: Any = spotify_client,
        user_id: Optional[str] = None,
    ):
        self.client = client
        # If user_id not provided, fetch from the API
        if user_id:
            self.user_id = user_id
            logger.info(f"Using provided user ID: {self.user_id}")
        else:
            self.user_id = self.get_current_user_id()

    def get_current_user_id(self) -> str:
        try:
            me = self.client.current_user()
            self.user_id = me.get("id")
            logger.info(f"Fetched current user ID: {self.user_id}")
        except Exception as e:
            logger.error(f"Failed to fetch current user ID: {e}")
            raise

    def fetch_playlist_tracks(self, playlist_id: str) -> List[Dict[str, Any]]:
        """
        Fetch all items from a Spotify playlist, including each item's 'added_at' timestamp.
        Handles pagination automatically.
        """
        tracks: List[Dict[str, Any]] = []
        page = 0
        resp = self.client.playlist_items(
            playlist_id,
            fields="items(added_at,track(id)),next",
        )
        logger.info(f"Fetched playlist items page {page} for {playlist_id}: {resp}")
        tracks.extend(resp.get("items", []))

        while resp.get("next"):
            page += 1
            resp = self.client.next(resp)
            logger.info(f"Fetched playlist items page {page} for {playlist_id}: {resp}")
            tracks.extend(resp.get("items", []))

        logger.info(f"Fetched {len(tracks)} tracks from playlist {playlist_id}")
        return tracks

    def add_tracks_to_playlist(self, playlist_id: str, track_ids: List[str]) -> None:
        """
        Add a batch of track IDs to a Spotify playlist.
        """
        logger.info(f"Adding {len(track_ids)} tracks to playlist {playlist_id}")
        try:
            response = self.client.playlist_add_items(playlist_id, track_ids)
            logger.info(f"Added tracks to playlist {playlist_id}: {response}")
        except Exception as e:
            logger.error(f"Failed to add tracks to playlist {playlist_id}: {e}")
            raise

    def get_playlist_metadata(self, playlist_id: str) -> Dict[str, Any]:
        """
        Fetch basic metadata for a Spotify playlist.
        """
        try:
            metadata = self.client.playlist(
                playlist_id,
                fields="id,name,description,snapshot_id",
            )
            logger.info(f"Fetched metadata for playlist {playlist_id}: {metadata}")
            return metadata
        except Exception as e:
            logger.error(f"Failed to fetch metadata for playlist {playlist_id}: {e}")
            raise

    def get_playlist_id_by_name(self, playlist_name: str) -> Optional[str]:
        """
        Return the first playlist ID matching `name` in the current user's library,
        or None if not found.
        """
        results = self.client.current_user_playlists(limit=50)
        while True:
            for pl in results.get("items", []):
                if pl.get("name", "").lower() == playlist_name.lower():
                    logger.info(f"Found playlist '{playlist_name}' → {pl['id']}")
                    return pl["id"]
            if results.get("next"):
                results = self.client.next(results)
            else:
                break

        logger.info(f"No playlist found with name '{name}'")
        return None
    
    def create_playlist_with_name(self, playlist_name: str, public: bool = False) -> str:
        """
        Ensure a playlist exists with the given name and return its ID.
        Creates it if it doesn’t exist.
        """
        existing_id = self.get_playlist_id_by_name(playlist_name)
        if existing_id:
            logger.info(f"Playlist '{playlist_name}' already exists → {existing_id}")
            return existing_id
        try:
            logger.info(f"Creating new playlist '{playlist_name}' (public={public}) for user {self.user_id}")
            new = self.client.user_playlist_create(
                user=self.user_id,
                name=playlist_name,
                public=public,
            )
            new_id = new.get("id")
            logger.info(f"Created playlist '{playlist_name}' → {new_id}")
            return new_id
        except Exception as e:
            logger.error(f"Failed to create playlist '{playlist_name}': {e}")
            raise