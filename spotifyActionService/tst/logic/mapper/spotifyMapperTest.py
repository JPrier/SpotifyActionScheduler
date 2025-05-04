import pytest
from logic.mapper.spotifyMapper import map_to_id_set


def test_map_empty_list() -> None:
    """
    Should return an empty set when given an empty list.
    """
    assert map_to_id_set([]) == set()


def test_map_single_item() -> None:
    """
    Should return a set with a single ID when given a single-item list.
    """
    items = [{"track": {"id": "abc"}}]
    assert map_to_id_set(items) == {"abc"}


def test_map_multiple_items_with_duplicates() -> None:
    """
    Should dedupe IDs: duplicates collapse into a single set entry.
    """
    items = [
        {"track": {"id": "1"}},
        {"track": {"id": "2"}},
        {"track": {"id": "1"}},
    ]
    result = map_to_id_set(items)
    assert result == {"1", "2"}


def test_map_missing_track_key_raises() -> None:
    """
    Should raise KeyError if the 'track' key is missing.
    """
    items = [{"no_track": {"id": "x"}}]
    with pytest.raises(KeyError):
        map_to_id_set(items)


def test_map_missing_id_key_raises() -> None:
    """
    Should raise KeyError if the 'id' key inside 'track' is missing.
    """
    items = [{"track": {"no_id": "x"}}]
    with pytest.raises(KeyError):
        map_to_id_set(items)
