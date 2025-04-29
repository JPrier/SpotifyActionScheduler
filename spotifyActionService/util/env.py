import os
from pathlib import Path
from dotenv import load_dotenv

# ── figure out where this file lives and back up into your project root
env_path = (Path(__file__).resolve().parent.parent / "spotify.env")
load_dotenv(dotenv_path=env_path)

def get_environ(key: str, default: str = None) -> str:
    """
    Fetches the environment variable for the given key. If not found, returns the default value.
    """
    return os.environ[key] if key in os.environ else default

def get_env(key: str, default: str = None) -> str:
    """
    Fetches the environment variable for the given key. If not found, returns the default value.
    """
    return os.getenv(key, default)