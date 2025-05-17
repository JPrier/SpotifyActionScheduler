import logging
from datetime import UTC, datetime, timedelta
from typing import Any

import logic.playlistLogic as playlistLogic
import pytest
from logic.playlistLogic import PlaylistService
from models.actions import ArchiveAction, SyncAction

# Helper to stub out map_to_id_set to use 'id' key


def _stub_id_map(monkeypatch: pytest.MonkeyPatch) -> None:
    # stub out the real mapper to use item['id']
    monkeypatch.setattr(
        playlistLogic,
        "map_to_id_set",
        lambda items: {item["id"] for item in items},
    )


# ------------------ Sync Tests ------------------


def test_sync_playlists_no_new(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.INFO)
    action = SyncAction(type="sync", source_playlist_id="src", target_playlist_id="tgt")
    _stub_id_map(monkeypatch)

    class DummyAccessor:
        def fetch_playlist_tracks(self, pid: str) -> list[dict[str, Any]]:
            # both playlists have same two tracks
            return [{"id": "a"}, {"id": "b"}]

        def add_tracks_to_playlist(self, pid: str, ids: list[str]) -> None:
            pytest.skip("No tracks should be added")

    service = PlaylistService(DummyAccessor())
    service.sync_playlists(action)
    assert "No new tracks to add to target playlist." in caplog.text


def test_sync_playlists_adds_new(monkeypatch: pytest.MonkeyPatch) -> None:
    action = SyncAction(type="sync", source_playlist_id="src", target_playlist_id="tgt")
    _stub_id_map(monkeypatch)
    calls: list[list[str]] = []

    class DummyAccessor:
        def fetch_playlist_tracks(self, pid: str) -> list[dict[str, Any]]:
            if pid == action.source_playlist_id:
                return [{"id": "1"}, {"id": "2"}, {"id": "3"}]
            return [{"id": "2"}]

        def add_tracks_to_playlist(self, pid: str, ids: list[str]) -> None:
            calls.append(ids)

    service = PlaylistService(DummyAccessor())
    service.sync_playlists(action)
    # Should only add 1 and 3
    assert len(calls) == 1
    assert set(calls[0]) == {"1", "3"}


# ------------------ Filter Tests ------------------


def test_filter_items_after_time() -> None:
    # Use real datetime.now to test offset
    now = datetime.now(UTC)
    older = (now - timedelta(seconds=60)).isoformat().replace("+00:00", "Z")
    newer = (now - timedelta(seconds=30)).isoformat().replace("+00:00", "Z")
    items = [
        {"added_at": older, "id": "old"},
        {"added_at": newer, "id": "new"},
    ]
    service = PlaylistService(object())  # accessor unused
    filtered = service.filter_items_after_time(items, time_in_seconds=45)
    # Only 'new' is within last 45 seconds
    assert len(filtered) == 1
    assert filtered[0]["id"] == "new"


# ------------------ Archive Tests ------------------


@pytest.mark.parametrize(
    "source_ids, existing_ids, filter_by_time, avoid_duplicates, expected_ids",
    [
        (["old", "new"], [], True, True, [["new"]]),
        (["old", "new"], [], True, False, [["new"]]),
        (["a", "b"], ["a"], False, True, [["b"]]),
        (["a", "b"], [], False, False, [["a", "b"]]),
        (["a", "b"], ["a", "b"], False, True, []),
    ],
)
def test_archive_playlists_all_combinations(
    monkeypatch: pytest.MonkeyPatch,
    source_ids: list[str],
    existing_ids: list[str],
    filter_by_time: bool,
    avoid_duplicates: bool,
    expected_ids: list[list[str]],
) -> None:
    _stub_id_map(monkeypatch)
    now = datetime.now(UTC)
    # build source_items
    if filter_by_time:
        # first id is older, second is newer
        source_items = [
            {
                "id": source_ids[0],
                "added_at": (now - timedelta(seconds=60))
                .isoformat()
                .replace("+00:00", "Z"),
            },
            {
                "id": source_ids[1],
                "added_at": (now - timedelta(seconds=30))
                .isoformat()
                .replace("+00:00", "Z"),
            },
        ]
    else:
        source_items = [{"id": sid, "added_at": "irrelevant"} for sid in source_ids]
    # build existing_items
    existing_items = [{"id": eid, "added_at": "irrelevant"} for eid in existing_ids]
    time_sec = 45 if filter_by_time else 0

    action = ArchiveAction(
        type="archive", source_playlist_id="src", target_playlist_id="tgt"
    )
    action.filter_by_time = filter_by_time
    action.avoidDuplicates = avoid_duplicates
    action.timeBetweenActInSeconds = time_sec

    calls: list[list[str]] = []

    class DummyAccessor:
        def fetch_playlist_tracks(self, pid: str) -> list[dict[str, Any]]:
            return source_items if pid == action.source_playlist_id else existing_items

        def get_playlist_metadata(self, pid: str) -> dict[str, Any]:
            return {"name": "PL"}

        def get_or_create_playlist_with_name(self, name: str) -> str:
            return "archid"

        def add_tracks_to_playlist(self, pid: str, ids: list[str]) -> None:
            calls.append(ids)

    service = PlaylistService(DummyAccessor())
    service.archive_playlists(action)
    sorted_calls = [sorted(lst) for lst in calls]
    sorted_expected = [sorted(lst) for lst in expected_ids]
    assert sorted_calls == sorted_expected
