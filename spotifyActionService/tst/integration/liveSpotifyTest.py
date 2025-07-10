import pytest
from accessor.spotifyAccessor import SpotifyAccessor
from dependency.spotifyClient import get_client


@pytest.mark.integration
def test_can_fetch_current_user() -> None:
    client = get_client()
    accessor = SpotifyAccessor(client)
    assert accessor.user_id is not None
