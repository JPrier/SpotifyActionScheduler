import os

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyOauthError
from util.env import get_environ


def get_client() -> Spotify:
    """Return an authenticated :class:`Spotify` client."""

    required = ["SPOTIPY_CLIENT_ID", "SPOTIPY_CLIENT_SECRET", "SPOTIPY_REDIRECT_URI"]
    missing = [name for name in required if not get_environ(name)]
    if missing:
        raise EnvironmentError(f"Missing environment variables: {', '.join(missing)}")

    scope = "playlist-read-private playlist-modify-public playlist-modify-private"
    auth_manager = SpotifyOAuth(
        client_id=get_environ("SPOTIPY_CLIENT_ID"),
        client_secret=get_environ("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=get_environ("SPOTIPY_REDIRECT_URI"),
        scope=scope,
    )

    refresh_token = get_environ("SPOTIPY_REFRESH_TOKEN")
    if refresh_token and not os.path.exists(".cache"):
        try:
            auth_manager.refresh_access_token(refresh_token)
        except SpotifyOauthError as exc:
            raise SpotifyOauthError(
                f"failed to refresh token: {exc}"
            ) from exc

    return Spotify(auth_manager=auth_manager)
