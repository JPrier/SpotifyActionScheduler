import logging
from typing import Any, Never

import pytest
from accessor.spotifyAccessor import SpotifyAccessor
from dependency.spotifyClient import spotify_client


@pytest.fixture
def sample_items_page() -> dict[str, Any]:
    return {
        "items": [
            {"added_at": "2025-01-01T00:00:00Z", "track": {"id": "t1"}},
            {"added_at": "2025-01-02T00:00:00Z", "track": {"id": "t2"}},
        ],
        "next": None,
    }


def test_init_with_user_id_skips_fetch(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.INFO)
    # If user_id is provided, client.current_user() should never be called
    monkeypatch.setattr(
        spotify_client,
        "current_user",
        lambda: (_ for _ in ()).throw(RuntimeError("should not be called")),
    )

    under_test = SpotifyAccessor(client=spotify_client, user_id="u999")
    assert under_test.user_id == "u999"
    assert "Using provided user ID: u999" in caplog.text


def test_get_current_user_id_success(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.INFO)
    # Stub out current_user() to return a known ID
    monkeypatch.setattr(spotify_client, "current_user", lambda: {"id": "u42"})

    under_test = SpotifyAccessor(
        client=spotify_client, user_id="u123"
    )  # skip init-fetch
    under_test.user_id = None  # clear it so get_current_user_id actually runs
    under_test.get_current_user_id()

    assert under_test.user_id == "u42"
    assert "Fetched current user ID: u42" in caplog.text


def test_get_current_user_id_failure(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.ERROR)

    # Simulate API failure
    def bad_current_user() -> None:
        raise RuntimeError("no auth")

    monkeypatch.setattr(spotify_client, "current_user", bad_current_user)

    under_test = SpotifyAccessor(client=spotify_client, user_id="u123")
    under_test.user_id = None

    with pytest.raises(RuntimeError):
        under_test.get_current_user_id()
    assert "Failed to fetch current user ID: no auth" in caplog.text


def test_fetch_playlist_tracks_single_page(
    monkeypatch: pytest.MonkeyPatch, sample_items_page: dict[str, Any]
) -> None:
    # stub out playlist_items to return our single page
    def fake_playlist_items(pid: str, fields: str) -> dict[str, Any]:
        assert pid == "pl123"
        assert fields == "items(added_at,track(id)),next"
        return sample_items_page

    # next() should never be called here, but stub it just in case
    monkeypatch.setattr(spotify_client, "playlist_items", fake_playlist_items)
    monkeypatch.setattr(
        spotify_client, "next", lambda resp: {"items": [], "next": None}
    )

    under_test = SpotifyAccessor(client=spotify_client, user_id="u999")

    tracks = under_test.fetch_playlist_tracks("pl123")

    # we should get back the same two items
    assert len(tracks) == 2
    assert tracks[0]["track"]["id"] == "t1"
    assert tracks[1]["added_at"] == "2025-01-02T00:00:00Z"


def test_fetch_playlist_tracks_multiple_pages(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    page1 = {"items": [{"added_at": "a", "track": {"id": "1"}}], "next": "url2"}
    page2 = {"items": [{"added_at": "b", "track": {"id": "2"}}], "next": None}

    monkeypatch.setattr(spotify_client, "playlist_items", lambda pid, fields: page1)
    monkeypatch.setattr(spotify_client, "next", lambda resp: page2)

    under_test = SpotifyAccessor(client=spotify_client, user_id="u999")

    tracks = under_test.fetch_playlist_tracks("plX")
    assert [t["track"]["id"] for t in tracks] == ["1", "2"]


def test_add_tracks_to_playlist_success(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.INFO)

    # fake add_items returns a dummy response
    monkeypatch.setattr(
        spotify_client, "playlist_add_items", lambda pid, ids: {"snapshot_id": "abc"}
    )

    under_test = SpotifyAccessor(client=spotify_client, user_id="u999")

    under_test.add_tracks_to_playlist("plA", ["x", "y", "z"])

    assert "Adding 3 tracks to playlist plA: ['x', 'y', 'z']" in caplog.text
    assert "Added tracks to playlist plA" in caplog.text


def test_add_tracks_to_playlist_failure(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.ERROR)

    def bad_add(pid: str, ids: list[str]) -> None:
        raise RuntimeError("API down")

    monkeypatch.setattr(spotify_client, "playlist_add_items", bad_add)

    under_test = SpotifyAccessor(client=spotify_client, user_id="u999")

    with pytest.raises(RuntimeError):
        under_test.add_tracks_to_playlist("pFAIL", ["1"])
    assert "Failed to add tracks to playlist pFAIL: API down" in caplog.text


def test_get_playlist_metadata_success(monkeypatch: pytest.MonkeyPatch) -> None:
    dummy = {"id": "p", "name": "MyList", "description": "desc", "snapshot_id": "s1"}
    monkeypatch.setattr(spotify_client, "playlist", lambda pid, fields: dummy)

    under_test = SpotifyAccessor(client=spotify_client, user_id="u999")

    md = under_test.get_playlist_metadata("p")
    assert md["name"] == "MyList"
    assert md["snapshot_id"] == "s1"


def test_get_playlist_metadata_failure(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.ERROR)

    def bad_meta(pid: str, fields: str) -> Never:
        raise ValueError("nope")

    monkeypatch.setattr(spotify_client, "playlist", bad_meta)

    under_test = SpotifyAccessor(client=spotify_client, user_id="u999")

    with pytest.raises(ValueError):
        under_test.get_playlist_metadata("p")
    assert "Failed to fetch metadata for playlist p: nope" in caplog.text


def test_get_playlist_id_by_name_found_on_first_page(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.INFO)
    # First page has the playlist
    page = {"items": [{"name": "MyList", "id": "p1"}], "next": None}
    monkeypatch.setattr(spotify_client, "current_user_playlists", lambda limit: page)

    under_test = SpotifyAccessor(client=spotify_client, user_id="u123")
    pid = under_test.get_playlist_id_by_name("MyList")

    assert pid == "p1"
    assert "Found playlist 'MyList' → p1" in caplog.text


def test_get_playlist_id_by_name_found_on_second_page(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    page1 = {"items": [], "next": "url2"}
    page2 = {"items": [{"name": "Other", "id": "p2"}], "next": None}

    monkeypatch.setattr(spotify_client, "current_user_playlists", lambda limit: page1)
    monkeypatch.setattr(spotify_client, "next", lambda resp: page2)

    under_test = SpotifyAccessor(client=spotify_client, user_id="u123")
    pid = under_test.get_playlist_id_by_name("Other")

    assert pid == "p2"


def test_get_playlist_id_by_name_not_found(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.INFO)
    # No items and no next
    monkeypatch.setattr(
        spotify_client,
        "current_user_playlists",
        lambda limit: {"items": [], "next": None},
    )

    under_test = SpotifyAccessor(client=spotify_client, user_id="u123")
    pid = under_test.get_playlist_id_by_name("Nothing")

    assert pid is None
    assert "No playlist found with name 'Nothing'" in caplog.text


def test_create_playlist_with_name_success(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.INFO)
    # Stub out user_playlist_create
    monkeypatch.setattr(
        spotify_client,
        "user_playlist_create",
        lambda user, name, public: {"id": "new123"},
    )

    under_test = SpotifyAccessor(client=spotify_client, user_id="u123")
    new_id = under_test.create_playlist_with_name("CoolList", public=True)

    assert new_id == "new123"
    assert "Creating new playlist 'CoolList' (public=True) for user u123" in caplog.text
    assert "Created playlist 'CoolList' → new123" in caplog.text


def test_create_playlist_with_name_failure(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.ERROR)

    def bad_create(user: str, name: str, public: bool) -> None:
        raise RuntimeError("quota")

    monkeypatch.setattr(spotify_client, "user_playlist_create", bad_create)

    under_test = SpotifyAccessor(client=spotify_client, user_id="u123")
    with pytest.raises(RuntimeError):
        under_test.create_playlist_with_name("BadList", public=False)

    assert "Failed to create playlist 'BadList': quota" in caplog.text


def test_get_or_create_playlist_with_name_existing(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.INFO)
    under_test = SpotifyAccessor(client=spotify_client, user_id="u123")

    # existing
    monkeypatch.setattr(under_test, "get_playlist_id_by_name", lambda name: "exists123")
    monkeypatch.setattr(
        under_test,
        "create_playlist_with_name",
        lambda name, public=False: (_ for _ in ()).throw(
            RuntimeError("should not be called")
        ),
    )

    pid = under_test.get_or_create_playlist_with_name("ExistList", public=False)
    assert pid == "exists123"
    assert "Playlist 'ExistList' already exists → exists123" in caplog.text


def test_get_or_create_playlist_with_name_creates(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.INFO)
    under_test = SpotifyAccessor(client=spotify_client, user_id="u123")

    monkeypatch.setattr(under_test, "get_playlist_id_by_name", lambda name: None)
    monkeypatch.setattr(
        under_test, "create_playlist_with_name", lambda name, public=False: "created456"
    )

    pid = under_test.get_or_create_playlist_with_name("NewList", public=True)
    assert pid == "created456"
    assert "Playlist 'NewList' not found, creating new one" in caplog.text
