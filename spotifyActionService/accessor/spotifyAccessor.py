from spotifyActionService.util.logger import logger
from spotifyActionService.accessor.spotifyClient import spotify_client as client

def convert_playlist_to_ordered_id_list(playlist_items: list) -> list:
    """
    Convert playlist items to a list of track IDs, sorted by the timestamp when they were added (ascending).
    Each item requires 'added_at' in ISO format and a nested 'track.id'.
    """
    # Filter out any non-track items and sort by added_at timestamp
    sorted_items = sorted(
        (item for item in playlist_items if item.get("track") and item.get("added_at")),
        key=lambda i: i["added_at"]
    )
    return [item["track"]["id"] for item in sorted_items]


def fetch_playlist_tracks(playlist_id: str) -> list:
    """
    Fetch all items from a Spotify playlist, including each item's 'added_at' timestamp.
    """
    tracks = []
    # Request only the fields we need to minimize payload
    resp = client.playlist_items(
        playlist_id,
        fields="items(added_at,track(id)),next"
    )
    tracks.extend(resp.get("items", []))
    while resp.get("next"):
        resp = client.next(resp)
        tracks.extend(resp.get("items", []))
    return tracks
