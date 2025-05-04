import logging

import pytest
import service.onDemandHandler as under_test


def test_main_invokes_parse_and_handle(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO)

    # prepare fake actions and record calls
    actions = ["act1", "act2"]
    calls: list = []

    def fake_parse(path: str) -> list[str]:
        calls.append(path)
        return actions

    def fake_handle(actions_arg: list) -> None:
        calls.append(actions_arg)

    # stub out parseActionFile and handleActions in onDemandHandler
    monkeypatch.setattr(
        under_test,
        "parseActionFile",
        fake_parse,
    )
    monkeypatch.setattr(
        under_test,
        "handleActions",
        fake_handle,
    )

    # run main
    under_test.main()

    # verify parseActionFile was called with the correct filepath
    assert calls and calls[0] == "spotifyActionService/actions.json"
    # verify handleActions was called with returned actions
    assert len(calls) > 1 and calls[1] is actions

    # verify log messages
    log = caplog.text
    assert "Starting on-demand handler..." in log
    assert "Parsing action file..." in log
    assert "Parsed 2 actions." in log
    assert "Actions: ['act1', 'act2']" in log
