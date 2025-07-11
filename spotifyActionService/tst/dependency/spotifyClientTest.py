import os

import dependency.spotifyClient as under_test
import pytest


class DummyOAuth:
    def __init__(self, *args: object, **kwargs: object) -> None:
        self.refreshed_with: list[str] = []

    def refresh_access_token(self, token: str) -> None:
        self.refreshed_with.append(token)


class DummySpotify:
    def __init__(self, auth_manager: DummyOAuth) -> None:
        self.auth_manager = auth_manager


def test_refresh_token_used_when_cache_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    # set required env vars
    monkeypatch.setenv("SPOTIPY_CLIENT_ID", "cid")
    monkeypatch.setenv("SPOTIPY_CLIENT_SECRET", "secret")
    monkeypatch.setenv("SPOTIPY_REDIRECT_URI", "uri")
    monkeypatch.setenv("SPOTIPY_REFRESH_TOKEN", "refresh")

    dummy = DummyOAuth()
    monkeypatch.setattr(under_test, "SpotifyOAuth", lambda **kwargs: dummy)
    monkeypatch.setattr(under_test, "Spotify", DummySpotify)

    monkeypatch.setattr(os.path, "exists", lambda path: False)

    client = under_test.get_client()
    assert client.auth_manager is dummy
    assert dummy.refreshed_with == ["refresh"]


