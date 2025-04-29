def map_to_id_set(playlist_items: list) -> set:
    """
    Convert playlist items to a set of track IDs.
    """
    return set([item["track"]["id"] for item in playlist_items])