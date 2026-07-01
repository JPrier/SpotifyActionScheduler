import pytest
import service.cli as cli_module
from click.testing import CliRunner


def test_cli_sync_invokes_do_sync(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runner = CliRunner()
    calls: list[tuple[str, str, bool]] = []
    # stub out do_sync
    monkeypatch.setattr(
        cli_module,
        "do_sync",
        lambda src, tgt, avoid_duplicates: calls.append((src, tgt, avoid_duplicates)),
    )

    result = runner.invoke(cli_module.cli, ["sync", "src123", "tgt456"])
    assert result.exit_code == 0
    assert calls == [("src123", "tgt456", True)]


def test_cli_sync_allow_duplicates_flag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runner = CliRunner()
    calls: list[tuple[str, str, bool]] = []
    monkeypatch.setattr(
        cli_module,
        "do_sync",
        lambda src, tgt, avoid_duplicates: calls.append((src, tgt, avoid_duplicates)),
    )

    result = runner.invoke(
        cli_module.cli,
        ["sync", "src1", "tgt1", "--allow-duplicates"],
    )
    assert result.exit_code == 0
    assert calls == [("src1", "tgt1", False)]


def test_cli_archive_defaults(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runner = CliRunner()
    calls: list[tuple[str, str, int, bool, bool]] = []
    monkeypatch.setattr(
        cli_module,
        "do_archive",
        lambda src, tgt, days, avoid_duplicates, filter_by_time: calls.append(
            (src, tgt, days, avoid_duplicates, filter_by_time)
        ),
    )

    result = runner.invoke(
        cli_module.cli,
        ["archive", "srcP", "tgtP"],
    )
    assert result.exit_code == 0
    assert calls == [("srcP", "tgtP", 30, True, True)]


def test_cli_archive_custom_flags(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runner = CliRunner()
    calls: list[tuple[str, str, int, bool, bool]] = []
    monkeypatch.setattr(
        cli_module,
        "do_archive",
        lambda src, tgt, days, avoid_duplicates, filter_by_time: calls.append(
            (src, tgt, days, avoid_duplicates, filter_by_time)
        ),
    )

    cmd = [
        "archive",
        "sID",
        "tID",
        "--days",
        "10",
        "--allow-duplicates",
        "--filter-time",
    ]
    result = runner.invoke(cli_module.cli, cmd)
    assert result.exit_code == 0
    # --allow-duplicates => avoid_duplicates=False
    # --filter-time => filter_by_time=False
    assert calls == [("sID", "tID", 10, False, False)]


def test_cli_sync_liked_defaults(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runner = CliRunner()
    calls: list[tuple[str, int, bool, int]] = []
    monkeypatch.setattr(
        cli_module,
        "do_sync_liked",
        lambda tgt, hours, avoid_duplicates, max_tracks: calls.append(
            (tgt, hours, avoid_duplicates, max_tracks)
        ),
    )

    result = runner.invoke(cli_module.cli, ["sync-liked", "tgt789"])
    assert result.exit_code == 0
    assert calls == [("tgt789", 24, True, 500)]


def test_cli_sync_liked_custom_flags(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runner = CliRunner()
    calls: list[tuple[str, int, bool, int]] = []
    monkeypatch.setattr(
        cli_module,
        "do_sync_liked",
        lambda tgt, hours, avoid_duplicates, max_tracks: calls.append(
            (tgt, hours, avoid_duplicates, max_tracks)
        ),
    )

    result = runner.invoke(
        cli_module.cli,
        [
            "sync-liked",
            "tgt1",
            "--hours",
            "12",
            "--allow-duplicates",
            "--max-tracks",
            "100",
        ],
    )
    assert result.exit_code == 0
    assert calls == [("tgt1", 12, False, 100)]


def test_cli_run_once_invokes_run_actions_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runner = CliRunner()
    calls: list[bool] = []
    monkeypatch.setattr(
        cli_module,
        "run_actions_once",
        lambda: calls.append(True),
    )

    result = runner.invoke(
        cli_module.cli,
        ["run-once"],
    )
    assert result.exit_code == 0
    assert calls == [True]


def test_cli_schedule_invokes_start_scheduled_actions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runner = CliRunner()
    calls: list[bool] = []
    monkeypatch.setattr(
        cli_module,
        "start_scheduled_actions",
        lambda: calls.append(True),
    )

    result = runner.invoke(cli_module.cli, ["schedule"])
    assert result.exit_code == 0
    assert calls == [True]
