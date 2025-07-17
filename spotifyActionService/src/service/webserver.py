from __future__ import annotations

import json
import os
from http import HTTPStatus

from accessor.configLoader import load_json_file
from flask import Flask, jsonify, request
from logic.actionValidator import (
    VALIDATION_SUCCESS,
    validate_data,
)


def create_app(actions_file: str = "spotifyActionService/actions.json") -> Flask:
    app = Flask(__name__)
    app.config["ACTIONS_FILE"] = actions_file

    def load_actions() -> dict:
        if os.path.exists(actions_file):
            return load_json_file(actions_file)
        return {"actions": []}

    def save_actions(data: dict) -> None:
        with open(actions_file, "w") as f:
            json.dump(data, f, indent=2)

    @app.get("/actions")
    def get_actions() -> tuple[dict, int]:
        return jsonify(load_actions()), HTTPStatus.OK

    @app.post("/actions")
    def add_action() -> tuple[dict, int]:
        data = load_actions()
        actions = data.setdefault("actions", [])
        action = request.get_json(force=True)
        actions.append(action)
        if validate_data(data) != VALIDATION_SUCCESS:
            return (
                jsonify({"status": "error", "message": "validation failed"}),
                HTTPStatus.BAD_REQUEST,
            )
        save_actions(data)
        return jsonify({"status": "ok"}), HTTPStatus.CREATED

    @app.put("/actions/<int:idx>")
    def update_action(idx: int) -> tuple[dict, int]:
        data = load_actions()
        actions = data.setdefault("actions", [])
        if not (0 <= idx < len(actions)):
            return (
                jsonify({"status": "error", "message": "index out of range"}),
                HTTPStatus.NOT_FOUND,
            )
        actions[idx] = request.get_json(force=True)
        if validate_data(data) != VALIDATION_SUCCESS:
            return (
                jsonify({"status": "error", "message": "validation failed"}),
                HTTPStatus.BAD_REQUEST,
            )
        save_actions(data)
        return jsonify({"status": "ok"}), HTTPStatus.OK

    @app.get("/validate")
    def validate() -> tuple[dict, int]:
        data = load_actions()
        code = validate_data(data)
        return jsonify({"code": code}), HTTPStatus.OK

    return app
