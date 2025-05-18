import json
from pathlib import Path

import pytest
from models.actions import Action, ActionType, ArchiveAction, SyncAction
from service.helper.actionHelper import ACTION_MAP, ActionProcessor


def test_parse_valid_actions(tmp_path: Path) -> None:
    data = {
        "actions": [
            {"type": "sync", "source_playlist_id": "s1", "target_playlist_id": "t1"},
            {"type": "archive", "source_playlist_id": "s2", "target_playlist_id": "t2"},
        ]
    }
    file = tmp_path / "actions.json"
    file.write_text(json.dumps(data), encoding="utf-8")

    processor = ActionProcessor(playlist_service=None)
    actions = processor.parse_action_file(str(file))
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

    processor = ActionProcessor(playlist_service=None)
    with pytest.raises(KeyError) as exc:
        processor.parse_action_file(str(file))
    assert "Missing 'type' in action" in str(exc.value)


def test_parse_unknown_type_raises_valueerror(tmp_path: Path) -> None:
    data = {"actions": [{"type": "foo"}]}
    file = tmp_path / "actions.json"
    file.write_text(json.dumps(data), encoding="utf-8")

    processor = ActionProcessor(playlist_service=None)
    with pytest.raises(ValueError) as exc:
        processor.parse_action_file(str(file))
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

    # Temporarily remove the mapping for SYNC
    monkeypatch.setitem(ACTION_MAP, ActionType.SYNC, None)

    processor = ActionProcessor(playlist_service=None)
    with pytest.raises(RuntimeError) as exc:
        processor.parse_action_file(str(file))
    assert "No class registered for action type" in str(exc.value)


def test_parse_invalid_params_raises_valueerror(tmp_path: Path) -> None:
    data = {"actions": [{"type": "sync", "source_playlist_id": "s"}]}
    file = tmp_path / "actions.json"
    file.write_text(json.dumps(data), encoding="utf-8")

    processor = ActionProcessor(playlist_service=None)
    with pytest.raises(ValueError) as exc:
        processor.parse_action_file(str(file))
    msg = str(exc.value)
    assert msg.startswith("Invalid params for <ActionType.SYNC")


def test_handle_action_dispatch() -> None:
    calls = []

    class DummyService:
        def sync_playlists(self, action: Action) -> None:
            calls.append(("sync", action))

        def archive_playlists(self, action: Action) -> None:
            calls.append(("archive", action))

    processor = ActionProcessor(playlist_service=DummyService())

    sync_action = SyncAction(
        type=ActionType.SYNC, source_playlist_id="s", target_playlist_id="t"
    )
    processor.handle_action(sync_action)
    assert calls == [("sync", sync_action)]

    calls.clear()
    archive_action = ArchiveAction(
        type=ActionType.ARCHIVE, source_playlist_id="s", target_playlist_id="t"
    )
    processor.handle_action(archive_action)
    assert calls == [("archive", archive_action)]


def test_handle_action_default(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = []

    class DummyService:
        def sync_playlists(self, action: Action) -> None:
            calls.append(("sync", action))

        def archive_playlists(self, action: Action) -> None:
            calls.append(("archive", action))

    processor = ActionProcessor(playlist_service=DummyService())

    class DummyAction:
        type = None

    processor.handle_action(DummyAction())
    assert calls == []


def test_handle_actions_iterates() -> None:
    calls = []
    processor = ActionProcessor(playlist_service=None)
    processor.handle_action = lambda action: calls.append(action)

    a1 = SyncAction(
        type=ActionType.SYNC, source_playlist_id="s1", target_playlist_id="t1"
    )
    a2 = ArchiveAction(
        type=ActionType.ARCHIVE, source_playlist_id="s2", target_playlist_id="t2"
    )
    processor.handle_actions([a1, a2])

    assert calls == [a1, a2]
