import json
from pathlib import Path

import pytest
import service.helper.actionHelper as under_test
from models.actions import (
    ActionType,
    ArchiveAction,
    SyncAction,
)
from service.helper.actionHelper import (
    handleAction,
    handleActions,
    parseActionFile,
)


def test_parse_valid_actions(tmp_path: Path) -> None:
    data = {
        "actions": [
            {"type": "sync", "source_playlist_id": "s1", "target_playlist_id": "t1"},
            {"type": "archive", "source_playlist_id": "s2", "target_playlist_id": "t2"},
        ]
    }
    file = tmp_path / "actions.json"
    file.write_text(json.dumps(data), encoding="utf-8")

    actions = parseActionFile(str(file))
    assert len(actions) == 2
    act1, act2 = actions
    assert isinstance(act1, SyncAction)
    assert act1.type == ActionType.SYNC
    assert act1.source_playlist_id == "s1"
    assert act1.target_playlist_id == "t1"
    assert isinstance(act2, ArchiveAction)
    assert act2.type == ActionType.ARCHIVE


def test_parse_missing_type_key_raises_keyerror(tmp_path: Path) -> None:
    data = {"actions": [{"source_playlist_id": "s", "target_playlist_id": "t"}]}
    file = tmp_path / "actions.json"
    file.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(KeyError) as exc:
        parseActionFile(str(file))
    assert "Missing 'type' in action" in str(exc.value)


def test_parse_unknown_type_raises_valueerror(tmp_path: Path) -> None:
    data = {"actions": [{"type": "foo"}]}
    file = tmp_path / "actions.json"
    file.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(ValueError) as exc:
        parseActionFile(str(file))
    assert "Unknown action type: foo" in str(exc.value)


def test_parse_unregistered_type_raises_runtimeerror(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data = {
        "actions": [
            {"type": "sync", "source_playlist_id": "s", "target_playlist_id": "t"}
        ]
    }
    file = tmp_path / "actions.json"
    file.write_text(json.dumps(data), encoding="utf-8")

    monkeypatch.setitem(under_test.ACTION_MAP, ActionType.SYNC, None)
    with pytest.raises(RuntimeError) as exc:
        parseActionFile(str(file))
    assert "No class registered for action type" in str(exc.value)


def test_parse_invalid_params_raises_valueerror(tmp_path: Path) -> None:
    data = {"actions": [{"type": "sync", "source_playlist_id": "s"}]}
    file = tmp_path / "actions.json"
    file.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(ValueError) as exc:
        parseActionFile(str(file))
    msg = str(exc.value)
    assert msg.startswith("Invalid params for <ActionType.SYNC")


def test_handleAction_sync(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list = []
    monkeypatch.setattr(
        under_test, "sync_playlists", lambda action: calls.append(("sync", action))
    )
    monkeypatch.setattr(
        under_test,
        "archive_playlists",
        lambda action: calls.append(("archive", action)),
    )

    action = SyncAction(
        type=ActionType.SYNC, source_playlist_id="s", target_playlist_id="t"
    )
    handleAction(action)

    assert calls == [("sync", action)]


def test_handleAction_archive(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list = []
    monkeypatch.setattr(
        under_test, "sync_playlists", lambda action: calls.append(("sync", action))
    )
    monkeypatch.setattr(
        under_test,
        "archive_playlists",
        lambda action: calls.append(("archive", action)),
    )

    action = ArchiveAction(
        type=ActionType.ARCHIVE, source_playlist_id="s", target_playlist_id="t"
    )
    handleAction(action)

    assert calls == [("archive", action)]


def test_handleAction_default(monkeypatch: pytest.MonkeyPatch) -> None:
    # Spy lists for sync/archive invocations
    sync_calls = []
    archive_calls = []

    # Stub out the real handlers
    monkeypatch.setattr(
        under_test, "sync_playlists", lambda action: sync_calls.append(action)
    )
    monkeypatch.setattr(
        under_test, "archive_playlists", lambda action: archive_calls.append(action)
    )

    # Make any object with .type that is neither SYNC nor ARCHIVE
    class Dummy:
        def __init__(self) -> None:
            self.type = None  # not ActionType.SYNC or ARCHIVE

    dummy = Dummy()
    # Should do absolutely nothing (no exceptions, no calls)
    under_test.handleAction(dummy)

    assert sync_calls == []
    assert archive_calls == []


def test_handleActions(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list = []
    monkeypatch.setattr(under_test, "handleAction", lambda action: calls.append(action))

    a1 = SyncAction(
        type=ActionType.SYNC, source_playlist_id="s1", target_playlist_id="t1"
    )
    a2 = ArchiveAction(
        type=ActionType.ARCHIVE, source_playlist_id="s2", target_playlist_id="t2"
    )
    handleActions([a1, a2])

    assert calls == [a1, a2]
