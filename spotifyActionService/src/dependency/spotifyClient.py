import os

from spotipy import Spotify
from spotipy.exceptions import SpotifyOauthError
from spotipy.oauth2 import SpotifyOAuth
from util.env import get_environ


def get_client() -> Spotify:
    """Return an authenticated :class:`Spotify` client."""

    required = ["SPOTIFY_CLIENT_ID", "SPOTIFY_CLIENT_SECRET", "SPOTIFY_REDIRECT_URI"]
    missing = [name for name in required if not get_environ(name)]
    if missing:
        raise OSError(f"Missing environment variables: {', '.join(missing)}")

    scope = "playlist-read-private playlist-modify-public playlist-modify-private"
    auth_manager = SpotifyOAuth(
        client_id=get_environ("SPOTIFY_CLIENT_ID"),
        client_secret=get_environ("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=get_environ("SPOTIFY_REDIRECT_URI"),
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
