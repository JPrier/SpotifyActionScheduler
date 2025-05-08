import logging
from typing import Any

import logic.playlistLogic as playlistLogic
import pytest
from logic.playlistLogic import PlaylistService
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

    # prepare a dummy list of items
    dummy_items = object()
    calls: list[Any] = []

    # fake accessor just returns the same dummy_items for any playlist
    class DummyAccessor:
        def fetch_playlist_tracks(self, pid: str) -> list[dict[str, Any]]:
            return dummy_items

        def add_tracks_to_playlist(self, pid: str, ids: list[str]) -> None:
            calls.append((pid, ids))

    # patch the mapper that lives in logic.playlistLogic
    monkeypatch.setattr(
        playlistLogic,
        "map_to_id_set",
        lambda items: {"a", "b"} if items is dummy_items else set(),
    )

    service = PlaylistService(DummyAccessor())
    service.sync_playlists(action)

    # verify no additions were made
    assert not calls
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

    # two distinct dummy payloads
    src_items = object()
    tgt_items = object()
    calls: list[Any] = []

    class DummyAccessor:
        def fetch_playlist_tracks(self, pid: str) -> list[dict[str, Any]]:
            return src_items if pid == action.source_playlist_id else tgt_items

        def add_tracks_to_playlist(self, pid: str, ids: list[str]) -> None:
            calls.append((pid, ids))

    # map_to_id_set returns 1,2,3 for source, and 2 for target
    monkeypatch.setattr(
        playlistLogic,
        "map_to_id_set",
        lambda items: {"1", "2", "3"} if items is src_items else {"2"},
    )

    service = PlaylistService(DummyAccessor())
    service.sync_playlists(action)

    # we should have added exactly 1 and 3
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
    # turn off the time filter so we don't need to mock filter_items_after_time
    action.filterByTime = False

    # dummy items payload
    dummy_items = [{"id": "x"}, {"id": "y"}]

    class DummyAccessor:
        def fetch_playlist_tracks(self, pid: str) -> list[dict[str, Any]]:
            return dummy_items

        def get_playlist_metadata(self, pid: str) -> dict[str, Any]:
            return {"name": "MyPlaylist"}

        def get_or_create_playlist_with_name(self, name: str) -> str:
            return "archive_pl_id"

        def add_tracks_to_playlist(self, pid: str, ids: list[str]) -> None:
            # no-op for logging
            pass

    # stub out map_to_id_set to pick up our two IDs
    monkeypatch.setattr(
        playlistLogic,
        "map_to_id_set",
        lambda items: {"x", "y"},
    )

    service = PlaylistService(DummyAccessor())
    service.archive_playlists(action)

    # verify the key log messages
    assert "Fetching source playlist items..." in caplog.text
    assert "Found 2 tracks in source playlist:" in caplog.text
    # verify the archive playlist name appears
    assert "Using archive playlist name: 'MyPlaylist-Archive'" in caplog.text
    # final log is "Archived 2 tracks to playlist 'MyPlaylist-Archive'..."
    assert "Archived 2 tracks to playlist" in caplog.text
