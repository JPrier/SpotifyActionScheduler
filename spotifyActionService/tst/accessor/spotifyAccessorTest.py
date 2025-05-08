import logging
import pytest
from accessor.spotifyAccessor import SpotifyAccessor
from dependency.spotifyClient import spotify_client

def test_fetch_playlist_tracks_single_page(monkeypatch, caplog):
    caplog.set_level(logging.INFO)
    # one‐page response, no pagination
    first_page = {"items": [{"track": {"id": "t1"}, "added_at": "2025-05-08T00:00:00Z"}], "next": None}
    monkeypatch.setattr(
        spotify_client,
        "playlist_items",
        lambda playlist_id, fields: first_page,
    )
    # ensure .next is never called
    monkeypatch.setattr(
        spotify_client,
        "next",
        lambda resp: pytest.skip("Should not paginate"),
    )

    svc = SpotifyAccessor(client=spotify_client, user_id="u1")
    tracks = svc.fetch_playlist_tracks("pl1")

    assert tracks == first_page["items"]
    assert "Fetched playlist items page 0 for pl1" in caplog.text
    assert "Fetched 1 tracks from playlist pl1" in caplog.text

def test_fetch_playlist_tracks_multiple_pages(monkeypatch, caplog):
    caplog.set_level(logging.INFO)
    # two‐page response
    page1 = {"items": [{"track": {"id": "t1"}}], "next": "url2"}
    page2 = {"items": [{"track": {"id": "t2"}}], "next": None}
    monkeypatch.setattr(
        spotify_client,
        "playlist_items",
        lambda playlist_id, fields: page1,
    )
    monkeypatch.setattr(
        spotify_client,
        "next",
        lambda resp: page2,
    )

    svc = SpotifyAccessor(client=spotify_client, user_id="u1")
    tracks = svc.fetch_playlist_tracks("plX")

    assert tracks == page1["items"] + page2["items"]
    assert "Fetched playlist items page 1 for plX" in caplog.text
    assert "Fetched 2 tracks from playlist plX" in caplog.text

def test_add_tracks_to_playlist_success(monkeypatch, caplog):
    caplog.set_level(logging.INFO)
    # stub success
    monkeypatch.setattr(
        spotify_client,
        "playlist_add_items",
        lambda playlist_id, ids: {"snapshot_id": "snap123"},
    )

    svc = SpotifyAccessor(client=spotify_client, user_id="u1")
    svc.add_tracks_to_playlist("plA", ["t1", "t2"])

    assert "Adding 2 tracks to playlist plA" in caplog.text
    assert "Added tracks to playlist plA: {'snapshot_id': 'snap123'}" in caplog.text

def test_add_tracks_to_playlist_failure(monkeypatch, caplog):
    caplog.set_level(logging.ERROR)

    def bad_add(playlist_id, ids):
        raise RuntimeError("add-failed")

    monkeypatch.setattr(spotify_client, "playlist_add_items", bad_add)

    svc = SpotifyAccessor(client=spotify_client, user_id="u1")
    with pytest.raises(RuntimeError):
        svc.add_tracks_to_playlist("plBad", ["tX"])
    assert "Failed to add tracks to playlist plBad: add-failed" in caplog.text

def test_get_playlist_metadata_success(monkeypatch, caplog):
    caplog.set_level(logging.INFO)
    fake_meta = {"id": "pMeta", "name": "MetaName", "snapshot_id": "s1"}
    monkeypatch.setattr(
        spotify_client,
        "playlist",
        lambda playlist_id, fields: fake_meta,
    )

    svc = SpotifyAccessor(client=spotify_client, user_id="u1")
    result = svc.get_playlist_metadata("pMeta")

    assert result is fake_meta
    assert "Fetched metadata for playlist pMeta: {'id': 'pMeta', 'name': 'MetaName', 'snapshot_id': 's1'}" in caplog.text

def test_get_playlist_metadata_failure(monkeypatch, caplog):
    caplog.set_level(logging.ERROR)

    def bad_meta(playlist_id, fields):
        raise RuntimeError("meta-error")

    monkeypatch.setattr(spotify_client, "playlist", bad_meta)

    svc = SpotifyAccessor(client=spotify_client, user_id="u1")
    with pytest.raises(RuntimeError):
        svc.get_playlist_metadata("pErr")
    assert "Failed to fetch metadata for playlist pErr: meta-error" in caplog.text
