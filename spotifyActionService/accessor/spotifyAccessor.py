from typing import List, Dict, Any
from spotifyActionService.util.logger import logger
from spotifyActionService.accessor.spotifyClient import spotify_client as client

def fetch_playlist_tracks(playlist_id: str) -> List[Dict[str, Any]]:
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

def add_tracks_to_playlist(playlist_id: str, track_ids: List[str]) -> None:
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

# ----- DOES NOT WORK ------
# Spotify has changed the API and the positions field is ignored.
# Currently, there is no info on whether this will be fixed or not.
# For now this will be left here for reference

# def remove_tracks_from_playlist(playlist_id: str, snapshot_id: str, duplicates: Dict[str, List[int]]) -> None:
#     """
#     Remove duplicate tracks from a Spotify playlist.
#     duplicates = {track_id: [position1, position2, ...]}
#     """
#     payload = [
#         { "uri": f"spotify:track:{track_id}", "positions": positions }
#         for track_id, positions in duplicates.items()
#     ]
#     logger.info(f"Removing duplicates from playlist {playlist_id}-{snapshot_id}: {payload}")
#     try:
#         response = client.playlist_remove_specific_occurrences_of_items(
#             playlist_id,
#             payload,
#             snapshot_id=snapshot_id
#         )
#         logger.info(f"Removed duplicates from playlist {playlist_id}-{snapshot_id}: {response}")
#     except Exception as e:
#         logger.error(f"Failed to remove duplicates {playlist_id}-{snapshot_id}:{payload} received error: {e}")
#         raise

def get_metadata(playlist_id: str) -> Dict[str, Any]:
    """
    Fetch metadata of a Spotify playlist.
    """
    try:
        metadata = client.playlist(playlist_id, fields="id,name,description,snapshot_id")
        logger.info(f"Fetched metadata for playlist {playlist_id}: {metadata}")
        return metadata
    except Exception as e:
        logger.error(f"Failed to fetch metadata for playlist {playlist_id}: {e}")
        raise