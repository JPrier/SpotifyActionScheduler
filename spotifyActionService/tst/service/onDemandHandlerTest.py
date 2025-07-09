import logging

import pytest
import service.onDemandHandler as under_test
from accessor.spotifyAccessor import SpotifyAccessor
from service.helper.actionHelper import ActionProcessor
from spotipy import Spotify


def test_main_invokes_parse_and_handle(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO)

    # prepare fake actions and record calls
    actions = ["act1", "act2"]
    calls: list[tuple[str, object]] = []

    # stub out the external methods on ActionProcessor
    def fake_parse(self: ActionProcessor, path: str) -> list[str]:
        calls.append(("parse", path))
        return actions

    def fake_handle(self: ActionProcessor, actions_arg: list[str]) -> None:
        calls.append(("handle", actions_arg))

    monkeypatch.setattr(
        ActionProcessor,
        "parse_action_file",
        fake_parse,
    )
    monkeypatch.setattr(
        ActionProcessor,
        "handle_actions",
        fake_handle,
    )

    # stub SpotifyAccessor to bypass OAuth interaction
    monkeypatch.setattr(
        SpotifyAccessor, "get_current_user_id", lambda self: "test_user"
    )

    def fake_init(self: SpotifyAccessor, client: Spotify) -> None:
        # initialize minimal state without network or input
        self.user_id = "test_user"
        self.client = None

    monkeypatch.setattr(
        SpotifyAccessor,
        "__init__",
        fake_init,
    )

    # stub get_client to avoid real OAuth setup
    monkeypatch.setattr(under_test.spotifyClient, "get_client", lambda: None)

    # run main (this will use our monkeypatched methods)
    under_test.main()

    # verify parse_action_file was called with the correct filepath
    assert calls[0] == ("parse", "spotifyActionService/actions.json")
    # verify handle_actions was called with the returned actions
    assert calls[1] == ("handle", actions)

    # verify log messages
    log = caplog.text
    assert "Starting on-demand handler..." in log
    assert "Parsing action file..." in log
    assert "Parsed 2 actions." in log
    assert "Actions: ['act1', 'act2']" in log
    assert "Handling actions..." in log
