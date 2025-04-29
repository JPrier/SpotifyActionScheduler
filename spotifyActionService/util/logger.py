import logging
from spotifyActionService.util.env import get_env

# Configure logging
LOG_LEVEL = get_env("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("SpotifyApp")