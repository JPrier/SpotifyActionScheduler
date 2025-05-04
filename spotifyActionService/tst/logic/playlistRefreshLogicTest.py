import logging
from typing import Any

import logic.playlistRefreshLogic as under_test
import pytest
from models.actions import ArchiveAction, SyncAction


def test_sync_playlists_no_new(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO)
    action = SyncAction(
        type="sync",
        source_playlist_id="src_pl",
        target_playlist_id="tgt_pl",
    )

    # stub imported functions in logic module
    dummy_items = object()
    monkeypatch.setattr(
        under_test,
        "fetch_playlist_tracks",
        lambda pid: dummy_items,
    )
    monkeypatch.setattr(
        under_test,
        "map_to_id_set",
        lambda items: {"a", "b"} if items is dummy_items else set(),
    )
    called: list[Any] = []
    monkeypatch.setattr(
        under_test,
        "add_tracks_to_playlist",
        lambda pid, ids: called.append((pid, ids)),
    )

    # execute
    under_test.sync_playlists(action)

    # verify no additions
    assert not called
    assert "No new tracks to add to target playlist." in caplog.text


def test_sync_playlists_adds_new_tracks(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO)
    action = SyncAction(
        type="sync",
        source_playlist_id="src_pl",
        target_playlist_id="tgt_pl",
    )

    # distinct dummy items for source and target
    src_items = object()
    tgt_items = object()
    monkeypatch.setattr(
        under_test,
        "fetch_playlist_tracks",
        lambda pid: src_items if pid == action.source_playlist_id else tgt_items,
    )
    monkeypatch.setattr(
        under_test,
        "map_to_id_set",
        lambda items: {"1", "2", "3"} if items is src_items else {"2"},
    )
    calls: list[Any] = []

    def fake_add(pid: str, ids: list[str]) -> None:
        calls.append((pid, ids))

    monkeypatch.setattr(
        under_test,
        "add_tracks_to_playlist",
        fake_add,
    )

    # execute
    under_test.sync_playlists(action)

    # validate additions
    assert len(calls) == 1
    target_id, track_list = calls[0]
    assert target_id == action.target_playlist_id
    assert set(track_list) == {"1", "3"}
    expected_msg = (
        f"Added {len(track_list)} tracks to "
        f"target playlist: {action.target_playlist_id}"
    )
    assert expected_msg in caplog.text


def test_archive_playlists_logs(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO)
    action = ArchiveAction(
        type="archive",
        source_playlist_id="src_pl",
        target_playlist_id="tgt_pl",
    )

    # stub for archive
    dummy_items = object()
    monkeypatch.setattr(
        under_test,
        "fetch_playlist_tracks",
        lambda pid: dummy_items,
    )
    monkeypatch.setattr(
        under_test,
        "map_to_id_set",
        lambda items: {"x", "y"},
    )

    # execute
    under_test.archive_playlists(action)

    # verify logs
    assert "Fetching source playlist items..." in caplog.text
    assert "Found 2 tracks in source playlist:" in caplog.text
    assert "'x'" in caplog.text and "'y'" in caplog.text
    assert "Archiving source playlist..." in caplog.text
