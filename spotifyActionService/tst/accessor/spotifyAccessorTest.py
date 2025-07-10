import logging
from typing import Any

import pytest
from accessor.spotifyAccessor import SpotifyAccessor


@pytest.fixture
def dummy_client() -> object:
    """
    A fake Spotipy client that implements all of the methods
    SpotifyAccessor will call. Tests can monkeypatch these
    methods as needed.
    """

    class DummyClient:
        def current_user(self) -> dict[str, Any]:
            return {"id": "dummy_user"}

        def playlist_items(self, playlist_id: str, fields: str) -> dict[str, Any]:
            # default empty page
            return {"items": [], "next": None}

        def next(self, resp: dict[str, Any]) -> dict[str, Any]:
            return {"items": [], "next": None}

        def playlist_add_items(
            self, playlist_id: str, track_ids: list[str]
        ) -> dict[str, Any]:
            return {"snapshot_id": "dummy_snapshot"}

        def playlist(self, playlist_id: str, fields: str) -> dict[str, Any]:
            return {"id": playlist_id}

        def current_user_playlists(self, limit: int) -> dict[str, Any]:
            return {"items": [], "next": None}

        def user_playlist_create(
            self, user: str, name: str, public: bool
        ) -> dict[str, Any]:
            return {"id": "new_dummy_id"}

    return DummyClient()


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
    caplog: pytest.LogCaptureFixture,
    dummy_client: object,
) -> None:
    caplog.set_level(logging.INFO)
    # If user_id is provided, .current_user() should never be called:
    dummy_client.current_user = lambda: (_ for _ in ()).throw(
        RuntimeError("called current_user")
    )

    under_test = SpotifyAccessor(client=dummy_client, user_id="u999")
    assert under_test.user_id == "u999"
    assert "Using provided user ID: u999" in caplog.text


def test_get_current_user_id_success(
    caplog: pytest.LogCaptureFixture,
    dummy_client: object,
) -> None:
    caplog.set_level(logging.INFO)
    dummy_client.current_user = lambda: {"id": "u42"}

    under_test = SpotifyAccessor(client=dummy_client, user_id="u123")
    under_test.user_id = None
    under_test.get_current_user_id()

    assert under_test.user_id == "u42"
    assert "Fetched current user ID: u42" in caplog.text


def test_get_current_user_id_failure(
    caplog: pytest.LogCaptureFixture,
    dummy_client: object,
) -> None:
    caplog.set_level(logging.ERROR)
    dummy_client.current_user = lambda: (_ for _ in ()).throw(RuntimeError("no auth"))

    under_test = SpotifyAccessor(client=dummy_client, user_id="u123")
    under_test.user_id = None
    with pytest.raises(RuntimeError):
        under_test.get_current_user_id()
    assert "Failed to fetch current user ID: no auth" in caplog.text


def test_fetch_playlist_tracks_single_page(
    sample_items_page: dict[str, Any],
    dummy_client: object,
) -> None:
    def fake_items(pid: str, fields: str) -> dict[str, Any]:
        assert pid == "pl123"
        assert fields == "items(added_at,track(id)),next"
        return sample_items_page

    dummy_client.playlist_items = fake_items
    dummy_client.next = lambda resp: {"items": [], "next": None}

    under_test = SpotifyAccessor(client=dummy_client, user_id="u999")
    tracks = under_test.fetch_playlist_tracks("pl123")

    assert len(tracks) == 2
    assert tracks[0]["track"]["id"] == "t1"
    assert tracks[1]["added_at"] == "2025-01-02T00:00:00Z"


def test_fetch_playlist_tracks_multiple_pages(
    dummy_client: object,
) -> None:
    page1 = {"items": [{"added_at": "a", "track": {"id": "1"}}], "next": "url2"}
    page2 = {"items": [{"added_at": "b", "track": {"id": "2"}}], "next": None}

    dummy_client.playlist_items = lambda pid, fields: page1
    dummy_client.next = lambda resp: page2

    under_test = SpotifyAccessor(client=dummy_client, user_id="u999")
    tracks = under_test.fetch_playlist_tracks("plX")
    assert [t["track"]["id"] for t in tracks] == ["1", "2"]


def test_add_tracks_to_playlist_success(
    caplog: pytest.LogCaptureFixture,
    dummy_client: object,
) -> None:
    caplog.set_level(logging.INFO)
    dummy_client.playlist_add_items = lambda pid, ids: {"snapshot_id": "abc"}

    under_test = SpotifyAccessor(client=dummy_client, user_id="u999")
    under_test.add_tracks_to_playlist("plA", ["x", "y", "z"])

    assert "Adding 3 tracks to playlist plA: ['x', 'y', 'z']" in caplog.text
    assert "Added tracks to playlist plA: {'snapshot_id': 'abc'}" in caplog.text


def test_add_tracks_to_playlist_failure(
    caplog: pytest.LogCaptureFixture,
    dummy_client: object,
) -> None:
    caplog.set_level(logging.ERROR)
    dummy_client.playlist_add_items = lambda pid, ids: (_ for _ in ()).throw(
        RuntimeError("API down")
    )

    under_test = SpotifyAccessor(client=dummy_client, user_id="u999")
    with pytest.raises(RuntimeError):
        under_test.add_tracks_to_playlist("pFAIL", ["1"])
    assert "Failed to add tracks to playlist pFAIL: API down" in caplog.text

def test_get_playlist_metadata_success(
    dummy_client: object,
) -> None:
    dummy = {"id": "p", "name": "MyList", "description": "desc", "snapshot_id": "s1"}
    dummy_client.playlist = lambda pid, fields: dummy

    under_test = SpotifyAccessor(client=dummy_client, user_id="u999")
    md = under_test.get_playlist_metadata("p")
    assert md["name"] == "MyList"
    assert md["snapshot_id"] == "s1"


def test_get_playlist_metadata_failure(
    caplog: pytest.LogCaptureFixture,
    dummy_client: object,
) -> None:
    caplog.set_level(logging.ERROR)
    dummy_client.playlist = lambda pid, fields: (_ for _ in ()).throw(
        ValueError("nope")
    )

    under_test = SpotifyAccessor(client=dummy_client, user_id="u999")
    with pytest.raises(ValueError):
        under_test.get_playlist_metadata("p")
    assert "Failed to fetch metadata for playlist p: nope" in caplog.text


def test_get_playlist_id_by_name_found_on_first_page(
    caplog: pytest.LogCaptureFixture,
    dummy_client: object,
) -> None:
    caplog.set_level(logging.INFO)
    dummy_client.current_user_playlists = lambda limit: {
        "items": [{"name": "MyList", "id": "p1"}],
        "next": None,
    }

    under_test = SpotifyAccessor(client=dummy_client, user_id="u123")
    pid = under_test.get_playlist_id_by_name("MyList")

    assert pid == "p1"
    assert "Found playlist 'MyList' → p1" in caplog.text


def test_get_playlist_id_by_name_found_on_second_page(
    dummy_client: object,
) -> None:
    page1 = {"items": [], "next": "url2"}
    page2 = {"items": [{"name": "Other", "id": "p2"}], "next": None}

    dummy_client.current_user_playlists = lambda limit: page1
    dummy_client.next = lambda resp: page2

    under_test = SpotifyAccessor(client=dummy_client, user_id="u123")
    pid = under_test.get_playlist_id_by_name("Other")
    assert pid == "p2"


def test_get_playlist_id_by_name_not_found(
    caplog: pytest.LogCaptureFixture,
    dummy_client: object,
) -> None:
    caplog.set_level(logging.INFO)
    dummy_client.current_user_playlists = lambda limit: {"items": [], "next": None}

    under_test = SpotifyAccessor(client=dummy_client, user_id="u123")
    pid = under_test.get_playlist_id_by_name("Nothing")

    assert pid is None
    assert "No playlist found with name 'Nothing'" in caplog.text


def test_create_playlist_with_name_success(
    caplog: pytest.LogCaptureFixture,
    dummy_client: object,
) -> None:
    caplog.set_level(logging.INFO)
    dummy_client.user_playlist_create = lambda user, name, public: {"id": "new123"}

    under_test = SpotifyAccessor(client=dummy_client, user_id="u123")
    new_id = under_test.create_playlist_with_name("CoolList", public=True)

    assert new_id == "new123"
    assert "Creating new playlist 'CoolList' (public=True) for user u123" in caplog.text
    assert "Created playlist 'CoolList' → new123" in caplog.text


def test_create_playlist_with_name_failure(
    caplog: pytest.LogCaptureFixture,
    dummy_client: object,
) -> None:
    caplog.set_level(logging.ERROR)
    dummy_client.user_playlist_create = lambda user, name, public: (
        _ for _ in ()
    ).throw(RuntimeError("quota"))

    under_test = SpotifyAccessor(client=dummy_client, user_id="u123")
    with pytest.raises(RuntimeError):
        under_test.create_playlist_with_name("BadList", public=False)
    assert "Failed to create playlist 'BadList': quota" in caplog.text


def test_get_or_create_playlist_with_name_existing(
    caplog: pytest.LogCaptureFixture,
    dummy_client: object,
) -> None:
    caplog.set_level(logging.INFO)
    under_test = SpotifyAccessor(client=dummy_client, user_id="u123")

    under_test.get_playlist_id_by_name = lambda name: "exists123"
    under_test.create_playlist_with_name = lambda name, public=False: (
        _ for _ in ()
    ).throw(RuntimeError("should not be called"))

    pid = under_test.get_or_create_playlist_with_name("ExistList", public=False)
    assert pid == "exists123"
    assert "Playlist 'ExistList' already exists → exists123" in caplog.text


def test_get_or_create_playlist_with_name_creates(
    caplog: pytest.LogCaptureFixture,
    dummy_client: object,
) -> None:
    caplog.set_level(logging.INFO)
    under_test = SpotifyAccessor(client=dummy_client, user_id="u123")

    under_test.get_playlist_id_by_name = lambda name: None
    under_test.create_playlist_with_name = lambda name, public=False: "created456"

    pid = under_test.get_or_create_playlist_with_name("NewList", public=True)
    assert pid == "created456"
    assert "Playlist 'NewList' not found, creating new one" in caplog.text
