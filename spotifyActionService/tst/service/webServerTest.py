import json
from http import HTTPStatus
from pathlib import Path

from logic.actionValidator import VALIDATION_SUCCESS
from service.webserver import create_app


def test_add_and_validate(tmp_path: Path) -> None:
    actions_file = tmp_path / "actions.json"
    app = create_app(str(actions_file))
    client = app.test_client()

    # invalid action -> validation fails
    resp = client.post("/actions", json={"type": "bogus"})
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    # valid add
    resp = client.post(
        "/actions",
        json={
            "type": "sync",
            "source_playlist_id": "s",
            "target_playlist_id": "t",
        },
    )
    assert resp.status_code == HTTPStatus.CREATED

    resp = client.get("/validate")
    assert resp.json == {"code": VALIDATION_SUCCESS}

    with actions_file.open() as f:
        data = json.load(f)
    assert data["actions"][0]["type"] == "sync"

    # update with invalid data
    resp = client.put("/actions/0", json={"type": "bogus"})
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    # update with valid data
    resp = client.put(
        "/actions/0",
        json={
            "type": "archive",
            "source_playlist_id": "s",
            "target_playlist_id": None,
        },
    )
    assert resp.status_code == HTTPStatus.OK
