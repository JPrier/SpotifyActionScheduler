import json
from pathlib import Path

import pytest
from accessor.configLoader import load_json_file


def test_load_valid_json(tmp_path: Path) -> None:
    # create a temporary JSON file
    payload = {"foo": [1, 2, 3], "bar": {"baz": "qux"}}
    json_file = tmp_path / "data.json"
    json_file.write_text(json.dumps(payload), encoding="utf-8")

    # call your loader
    result = load_json_file(str(json_file))
    assert result == payload


def test_file_not_found(tmp_path: Path) -> None:
    missing = tmp_path / "does_not_exist.json"
    with pytest.raises(FileNotFoundError):
        load_json_file(str(missing))


def test_invalid_json(tmp_path: Path) -> None:
    # create a file whose contents aren’t valid JSON
    bad = tmp_path / "bad.json"
    bad.write_text("{ not: valid, json }", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        load_json_file(str(bad))


def test_propagates_other_io_errors(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    # simulate an IOError during open()
    dummy = tmp_path / "dummy.json"
    dummy.write_text("{}", encoding="utf-8")

    # monkeypatch open() to raise ZeroDivisionError
    monkeypatch.setattr(
        "builtins.open",
        lambda *args, **kwargs: 1/0,
    )

    with pytest.raises(ZeroDivisionError):
        load_json_file(str(dummy))
