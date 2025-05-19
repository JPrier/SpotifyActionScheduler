# spotifyActionService/tst/service/mainHandlerTest.py

from typing import Any

import pytest
import service.mainHandler as under_test
from accessor.spotifyAccessor import SpotifyAccessor
from dependency import spotifyClient
from logic import playlistLogic
from models.actions import Action, ActionType, ArchiveAction, SyncAction
from service import onDemandHandler, schedulerHandler


@pytest.fixture(autouse=True)
def _stub_spotify_clients(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Dummy client whose .current_user() won't call the network
    class DummyClient:
        def current_user(self) -> dict[str, Any]:
            return {"id": "dummy_user"}

    # stub get_client()
    monkeypatch.setattr(
        spotifyClient,
        "get_client",
        lambda: DummyClient(),
    )

    # stub out fetch of user_id in the accessor
    monkeypatch.setattr(
        SpotifyAccessor,
        "get_current_user_id",
        lambda self: setattr(self, "user_id", "dummy_user"),
    )


def test_do_sync(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    calls: list[Any] = []

    class DummyService:
        def __init__(self, accessor: Action) -> None:
            calls.append(("init", accessor))

        def sync_playlists(self, action: Action) -> None:
            calls.append(("sync", action))

    # stub PlaylistService
    monkeypatch.setattr(
        playlistLogic,
        "PlaylistService",
        DummyService,
    )

    under_test.do_sync("SRC", "TGT", avoid_duplicates=False)

    out = capsys.readouterr().out.strip()
    assert out == "✅ Synced from 'SRC' → 'TGT'"

    # the second call should be our sync
    kind, action = calls[1]
    assert kind == "sync"

    assert isinstance(action, SyncAction)
    assert action.type == ActionType.SYNC
    assert action.source_playlist_id == "SRC"
    assert action.target_playlist_id == "TGT"
    assert action.avoid_duplicates is False


def test_do_archive(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    import logic.playlistLogic as pl_logic

    calls: list[Any] = []

    class DummyService:
        def __init__(self, accessor: SpotifyAccessor) -> None:
            calls.append(("init", accessor))

        def archive_playlists(self, action: Action) -> None:
            calls.append(("archive", action))

    monkeypatch.setattr(
        pl_logic,
        "PlaylistService",
        DummyService,
    )

    import service.mainHandler as mh

    mh.do_archive("SRC2", "TGT2", days=5, avoid_duplicates=True, filter_by_time=False)

    out = capsys.readouterr().out.strip()
    assert out == "✅ Archived from 'SRC2' → 'TGT2'"

    kind, action = calls[1]
    assert kind == "archive"

    assert isinstance(action, ArchiveAction)
    assert action.type == ActionType.ARCHIVE
    assert action.source_playlist_id == "SRC2"
    assert action.target_playlist_id == "TGT2"
    assert action.timeBetweenActInSeconds == 5 * 24 * 3600
    assert action.avoid_duplicates is True
    assert action.filter_by_time is False


def test_run_actions_once(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[bool] = []
    monkeypatch.setattr(onDemandHandler, "main", lambda: calls.append(True))

    under_test.run_actions_once()
    assert calls == [True]


def test_start_scheduled_actions(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[bool] = []
    monkeypatch.setattr(schedulerHandler, "main", lambda: calls.append(True))

    under_test.start_scheduled_actions()
    assert calls == [True]
