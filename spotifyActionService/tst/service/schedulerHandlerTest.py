import time
from collections.abc import Callable

import pytest
import schedule
import service.schedulerHandler as under_test
from models.actions import Action
from service.schedulerHandler import (
    SLEEP_TIME_IN_SECONDS,
    main,
    schedule_action,
)


def test_schedule_action_creates_job(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list = []

    class FakeJob:
        def __init__(self, interval: int) -> None:
            self.interval = interval
            self.seconds = self

        def do(self, func: Callable[[Action], None], arg: Action) -> "FakeJob":
            calls.append((self.interval, func, arg))
            return self

    monkeypatch.setattr(
        schedule,
        "every",
        lambda n: FakeJob(n),
    )

    dummy = Action(type=None, timeBetweenActInSeconds=5)  # type can be None for test
    schedule_action(dummy)

    assert calls == [(5, under_test.handleAction, dummy)]


def test_main_schedules_and_runs_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # stub get_actions
    actions = ["x", "y"]
    monkeypatch.setattr(
        under_test,
        "get_actions",
        lambda: actions,
    )

    # record schedule_action calls
    scheduled: list = []
    monkeypatch.setattr(
        under_test,
        "schedule_action",
        lambda act: scheduled.append(act),
    )

    run_count = {"count": 0}

    def fake_run_pending() -> None:
        if run_count["count"] >= 1:
            raise KeyboardInterrupt()
        run_count["count"] += 1

    monkeypatch.setattr(
        schedule,
        "run_pending",
        fake_run_pending,
    )

    # stub sleep to no-op
    monkeypatch.setattr(
        time,
        "sleep",
        lambda s: None,
    )

    # run main and expect KeyboardInterrupt to break loop
    with pytest.raises(KeyboardInterrupt):
        main()

    # ensure scheduling happened for both actions
    assert scheduled == actions
    # ensure one iteration of run_pending
    assert run_count["count"] == 1
    # ensure sleep constant is used
    assert SLEEP_TIME_IN_SECONDS == 1
