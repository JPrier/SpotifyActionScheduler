from util.env import get_environ
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

# Spotify auth and client setup
scope = "playlist-read-private playlist-modify-public playlist-modify-private"
auth_manager = SpotifyOAuth(
    client_id=get_environ("SPOTIPY_CLIENT_ID"),
    client_secret=get_environ("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=get_environ("SPOTIPY_REDIRECT_URI"),
    scope=scope,
)
spotify_client = Spotify(auth_manager=auth_manager)
