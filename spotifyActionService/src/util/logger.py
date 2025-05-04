import logging

from util.env import get_env

# Configure logging
LOG_LEVEL = get_env("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s %(levelname)s %(name)s "
    + "[%(filename)s:%(lineno)d] --- %(message)s",
)
logger = logging.getLogger("SpotifyActionService")
