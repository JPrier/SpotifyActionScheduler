"""Integration tests that hit the real Spotify API."""

import os

import pytest
from accessor.spotifyAccessor import SpotifyAccessor
from dependency.spotifyClient import get_client
from spotipy.exceptions import SpotifyOauthError


@pytest.mark.integration
def test_can_fetch_current_user() -> None:
    """Verify we can fetch the current user ID when credentials are present."""

    # When running in CI without a cached token or refresh token, Spotipy will
    # attempt to open a browser for authentication and block waiting for user
    # input. To avoid hanging the workflow, fail fast when no token cache or
    # refresh token is available.
    cache_exists = os.path.exists(".cache")
    has_refresh = os.getenv("SPOTIPY_REFRESH_TOKEN")
    if not cache_exists and not has_refresh:
        pytest.fail("Spotify auth token not available")

    try:
        client = get_client()
        accessor = SpotifyAccessor(client)
    except (OSError, SpotifyOauthError) as exc:
        pytest.fail(f"Spotify auth failed: {exc}")

    assert accessor.user_id is not None
