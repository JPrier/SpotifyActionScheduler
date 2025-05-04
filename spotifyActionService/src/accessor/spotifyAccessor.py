from typing import Any

from accessor.spotifyClient import spotify_client as client
from util.logger import logger


def fetch_playlist_tracks(playlist_id: str) -> list[dict[str, Any]]:
    """
    Fetch all items from a Spotify playlist, including each item's 'added_at' timestamp.
    """
    tracks = []
    # Request only the fields we need to minimize payload
    resp = client.playlist_items(
        playlist_id,
        fields="items(added_at,track(id)),next",
    )
    logger.info(f"Fetched playlist items page 0: {resp}")
    tracks.extend(resp.get("items", []))
    while resp.get("next"):
        resp = client.next(resp)
        logger.info(f"Fetched playlist items page: {resp}")
        tracks.extend(resp.get("items", []))
    logger.info(f"Fetched {len(tracks)} tracks from playlist {playlist_id}: {tracks}")
    return tracks


def add_tracks_to_playlist(playlist_id: str, track_ids: list[str]) -> None:
    """
    Add tracks to a Spotify playlist.
    """
    logger.info(f"Adding tracks to playlist {playlist_id}: {track_ids}")
    try:
        response = client.playlist_add_items(playlist_id, track_ids)
        logger.info(f"Added tracks to playlist {playlist_id}: {response}")
    except Exception as e:
        logger.error(f"Failed to add tracks to playlist {playlist_id}: {e}")
        raise


def get_metadata(playlist_id: str) -> dict[str, Any]:
    """
    Fetch metadata of a Spotify playlist.
    """
    try:
        metadata = client.playlist(
            playlist_id, fields="id,name,description,snapshot_id"
        )
        logger.info(f"Fetched metadata for playlist {playlist_id}: {metadata}")
        return metadata
    except Exception as e:
        logger.error(f"Failed to fetch metadata for playlist {playlist_id}: {e}")
        raise
