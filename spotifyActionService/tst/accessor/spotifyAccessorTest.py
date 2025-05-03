import pytest
import logging
from accessor.spotifyClient import spotify_client
from accessor.spotifyAccessor import (
    fetch_playlist_tracks,
    add_tracks_to_playlist,
    get_metadata,
)

@pytest.fixture
def sample_items_page():
    return {
        "items": [
            {"added_at": "2025-01-01T00:00:00Z", "track": {"id": "t1"}},
            {"added_at": "2025-01-02T00:00:00Z", "track": {"id": "t2"}},
        ],
        "next": None,
    }

def test_fetch_playlist_tracks_single_page(monkeypatch, sample_items_page):
    # stub out playlist_items to return our single page
    def fake_playlist_items(pid, fields):
        assert pid == "pl123"
        assert fields == "items(added_at,track(id)),next"
        return sample_items_page

    # next() should never be called here, but stub it just in case
    monkeypatch.setattr(
        spotify_client, 
        "playlist_items", 
        fake_playlist_items
    )
    monkeypatch.setattr(
        spotify_client, 
        "next", 
        lambda resp: {"items": [], "next": None}
    )

    tracks = fetch_playlist_tracks("pl123")

    # we should get back the same two items
    assert len(tracks) == 2
    assert tracks[0]["track"]["id"] == "t1"
    assert tracks[1]["added_at"] == "2025-01-02T00:00:00Z"

def test_fetch_playlist_tracks_multiple_pages(monkeypatch):
    page1 = {"items": [{"added_at":"a","track":{"id":"1"}}], "next": "url2"}
    page2 = {"items": [{"added_at":"b","track":{"id":"2"}}], "next": None}

    monkeypatch.setattr(spotify_client, "playlist_items", lambda pid, fields: page1)
    monkeypatch.setattr(spotify_client, "next", lambda resp: page2)

    tracks = fetch_playlist_tracks("plX")
    assert [t["track"]["id"] for t in tracks] == ["1", "2"]

def test_add_tracks_to_playlist_success(monkeypatch, caplog):
    caplog.set_level(logging.INFO)

    # fake add_items returns a dummy response
    monkeypatch.setattr(
        spotify_client, 
        "playlist_add_items", 
        lambda pid, ids: {"snapshot_id": "abc"}
    )
    add_tracks_to_playlist("plA", ["x","y","z"])
    # make sure it logged the call
    assert "Adding tracks to playlist plA: ['x', 'y', 'z']" in caplog.text
    assert "Added tracks to playlist plA" in caplog.text

def test_add_tracks_to_playlist_failure(monkeypatch, caplog):
    caplog.set_level(logging.ERROR)
    def bad_add(pid, ids):
        raise RuntimeError("API down")
    monkeypatch.setattr(spotify_client, "playlist_add_items", bad_add)

    with pytest.raises(RuntimeError):
        add_tracks_to_playlist("pFAIL", ["1"])
    assert "Failed to add tracks to playlist pFAIL: API down" in caplog.text

def test_get_metadata_success(monkeypatch):
    dummy = {"id":"p","name":"MyList","description":"desc","snapshot_id":"s1"}
    monkeypatch.setattr(spotify_client, "playlist", lambda pid, fields: dummy)

    md = get_metadata("p")
    assert md["name"] == "MyList"
    assert md["snapshot_id"] == "s1"

def test_get_metadata_failure(monkeypatch, caplog):
    caplog.set_level(logging.ERROR)
    def bad_meta(pid, fields):
        raise ValueError("nope")
    monkeypatch.setattr(spotify_client, "playlist", bad_meta)

    with pytest.raises(ValueError):
        get_metadata("p")
    assert "Failed to fetch metadata for playlist p: nope" in caplog.text
