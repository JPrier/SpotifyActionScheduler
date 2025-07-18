import logic.actionValidator as under_test
import pytest
from _pytest.capture import CaptureFixture


def test_validate_json_load_error(
    monkeypatch: pytest.MonkeyPatch,
    capsys: CaptureFixture,
) -> None:
    # Simulate load_json_file raising
    monkeypatch.setattr(
        under_test,
        "load_json_file",
        lambda path: (_ for _ in ()).throw(RuntimeError("boom")),
    )

    code = under_test.validate("dummy.json")
    captured = capsys.readouterr()
    assert code == 1
    assert "[ERROR] Unable to load JSON: boom" in captured.err


def test_validate_missing_actions_key(
    monkeypatch: pytest.MonkeyPatch,
    capsys: CaptureFixture,
) -> None:
    monkeypatch.setattr(
        under_test,
        "load_json_file",
        lambda path: {"not_actions": []},
    )

    code = under_test.validate("dummy.json")
    captured = capsys.readouterr()
    assert code == 1
    assert "[ERROR] Top-level 'actions' key missing or not a list." in captured.err


def test_validate_actions_not_list(
    monkeypatch: pytest.MonkeyPatch,
    capsys: CaptureFixture,
) -> None:
    monkeypatch.setattr(
        under_test,
        "load_json_file",
        lambda path: {"actions": "nope"},
    )

    code = under_test.validate("dummy.json")
    captured = capsys.readouterr()
    assert code == 1
    assert "[ERROR] Top-level 'actions' key missing or not a list." in captured.err


def test_validate_action_not_object(
    monkeypatch: pytest.MonkeyPatch,
    capsys: CaptureFixture,
) -> None:
    monkeypatch.setattr(
        under_test,
        "load_json_file",
        lambda path: {"actions": [1]},
    )

    code = under_test.validate("dummy.json")
    captured = capsys.readouterr()
    assert code == 1
    assert "[VALIDATION FAILED]" in captured.err
    assert "actions[0]: 1 is not of type 'object'" in captured.err


def test_validate_missing_type_field(
    monkeypatch: pytest.MonkeyPatch,
    capsys: CaptureFixture,
) -> None:
    monkeypatch.setattr(
        under_test,
        "load_json_file",
        lambda path: {"actions": [{}]},
    )

    code = under_test.validate("dummy.json")
    captured = capsys.readouterr()
    assert code == 1
    assert "[VALIDATION FAILED]" in captured.err
    assert "actions[0]: 'type' is a required property" in captured.err


def test_validate_unknown_type(
    monkeypatch: pytest.MonkeyPatch,
    capsys: CaptureFixture,
) -> None:
    monkeypatch.setattr(
        under_test,
        "load_json_file",
        lambda path: {"actions": [{"type": "bogus"}]},
    )

    code = under_test.validate("dummy.json")
    captured = capsys.readouterr()
    assert code == 1
    assert "[VALIDATION FAILED]" in captured.err
    assert "actions[0].type: 'bogus' is not one of ['sync', 'archive']" in captured.err




def test_validate_invalid_params(
    monkeypatch: pytest.MonkeyPatch,
    capsys: CaptureFixture,
) -> None:
    monkeypatch.setattr(
        under_test,
        "load_json_file",
        lambda path: {"actions": [{"type": "sync"}]},
    )

    code = under_test.validate("dummy.json")
    captured = capsys.readouterr()
    assert code == 1
    assert "[VALIDATION FAILED]" in captured.err
    assert "actions[0]: {'type': 'sync'} is not valid under any of the given schemas" in captured.err


def test_validate_success(
    monkeypatch: pytest.MonkeyPatch,
    capsys: CaptureFixture,
) -> None:
    monkeypatch.setattr(
        under_test,
        "load_json_file",
        lambda path: {
            "actions": [
                {
                    "type": "sync",
                    "source_playlist_id": "s",
                    "target_playlist_id": "t",
                }
            ]
        },
    )

    code = under_test.validate("dummy.json")
    captured = capsys.readouterr()
    assert code == 0
    assert "✅ Validation succeeded: all actions are well-formed." in captured.out
