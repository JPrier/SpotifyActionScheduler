import time
from collections.abc import Callable

import pytest
import schedule
import service.schedulerHandler as under_test
from accessor.spotifyAccessor import SpotifyAccessor
from models.actions import Action
from service.schedulerHandler import (
    SLEEP_TIME_IN_SECONDS,
    main,
    schedule_action,
)
from spotipy import Spotify


class DummyProcessor:
    def handle_action(self, action: Action) -> None:
        # no-op
        ...


def test_schedule_action_creates_job(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = []

    class FakeJob:
        def __init__(self, interval: int) -> None:
            self.interval = interval
            self.seconds = self  # match the .seconds property

        def do(self, func: Callable[[Action], None], arg: Action) -> "FakeJob":
            calls.append((self.interval, func, arg))
            return self

    # mock external schedule.every
    monkeypatch.setattr(schedule, "every", lambda n: FakeJob(n))

    dummy_processor = DummyProcessor()
    dummy_action = Action(type=None, timeBetweenActInSeconds=5)

    # call the real schedule_action
    schedule_action(dummy_processor, dummy_action)

    assert calls == [(5, dummy_processor.handle_action, dummy_action)]


def test_main_schedules_and_runs_once(monkeypatch: pytest.MonkeyPatch) -> None:
    # 0) stub SpotifyAccessor to bypass OAuth interaction
    monkeypatch.setattr(
        SpotifyAccessor, "get_current_user_id", lambda self: "test_user"
    )

    def fake_init(self: SpotifyAccessor, client: Spotify) -> None:
        self.user_id = "test_user"
        self.client = None

    monkeypatch.setattr(
        SpotifyAccessor,
        "__init__",
        fake_init,
    )

    # stub get_client to avoid real OAuth setup
    monkeypatch.setattr(under_test.spotifyClient, "get_client", lambda: None)

    # 1) stub external ActionProcessor.parse_action_file
    actions = [
        Action(type=None, timeBetweenActInSeconds=3),
        Action(type=None, timeBetweenActInSeconds=7),
    ]
    monkeypatch.setattr(
        under_test.ActionProcessor,
        "parse_action_file",
        lambda self, path: actions,
    )

    # 2) capture calls to schedule.every
    calls = []

    class FakeJob:
        def __init__(self, interval: int) -> None:
            self.interval = interval
            self.seconds = self

        def do(self, func: Callable, arg: any) -> "FakeJob":
            calls.append((self.interval, func, arg))
            return self

    monkeypatch.setattr(schedule, "every", lambda n: FakeJob(n))

    # 3) stub schedule.run_pending to break after one iteration
    run_count = {"count": 0}

    def fake_run_pending() -> None:
        if run_count["count"] >= 1:
            raise KeyboardInterrupt()
        run_count["count"] += 1

    monkeypatch.setattr(schedule, "run_pending", fake_run_pending)

    # 4) stub external time.sleep
    monkeypatch.setattr(time, "sleep", lambda s: None)

    # run main — it should schedule both actions, run one loop, then raise
    with pytest.raises(KeyboardInterrupt):
        main()

    # assertions
    assert run_count["count"] == 1, "run_pending should be called exactly once"
    # two actions scheduled
    assert len(calls) == 2
    # check first action
    interval1, func1, arg1 = calls[0]
    assert interval1 == 3
    assert arg1 is actions[0]
    assert func1.__name__ == "handle_action"
    # check second action
    interval2, func2, arg2 = calls[1]
    assert interval2 == 7
    assert arg2 is actions[1]
    assert func2.__name__ == "handle_action"
    # make sure the sleep constant didn't change
    assert SLEEP_TIME_IN_SECONDS == 1
