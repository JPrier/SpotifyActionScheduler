import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="spotifyActionService/spotify.env")


def get_environ(key: str, default: str = None) -> str:
    """
    Fetches the environment variable for the given key. 
    If not found, returns the default value.
    """
    return os.environ[key] if key in os.environ else default


def get_env(key: str, default: str = None) -> str:
    """
    Fetches the environment variable for the given key. 
    If not found, returns the default value.
    """
    return os.getenv(key, default)
