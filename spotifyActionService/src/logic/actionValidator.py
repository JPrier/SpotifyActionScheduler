#!/usr/bin/env python3
import sys

from accessor.configLoader import load_json_file
from models.actions import ACTION_MAP, ActionType


def validate(filepath: str) -> int:
    # 1) Load the JSON (reports parse errors)
    try:
        data = load_json_file(filepath)
    except Exception as e:
        print(f"[ERROR] Unable to load JSON: {e}", file=sys.stderr)
        return 1

    # 2) Ensure top-level "actions" is present and is a list
    if "actions" not in data or not isinstance(data["actions"], list):
        print("[ERROR] Top-level 'actions' key missing or not a list.", file=sys.stderr)
        return 1

    errors: list[str] = []
    for idx, raw in enumerate(data["actions"]):
        ctx = f"actions[{idx}]"
        if not isinstance(raw, dict):
            errors.append(f"{ctx}: not an object")
            continue

        # 3) Validate the type enum
        typ = raw.get("type")
        if typ is None:
            errors.append(f"{ctx}: missing 'type' field")
            continue
        try:
            a_type = ActionType(typ)
        except ValueError:
            errors.append(f"{ctx}: unknown action type '{typ}'")
            continue

        # 4) Find the corresponding dataclass
        cls = ACTION_MAP.get(a_type)
        if cls is None:
            errors.append(f"{ctx}: no dataclass registered for type '{typ}'")
            continue

        # 5) Try to instantiate — dataclasses will raise on missing/wrong params
        params = {k: v for k, v in raw.items() if k != "type"}
        try:
            cls(type=a_type, **params)
        except TypeError as e:
            errors.append(f"{ctx}: invalid parameters → {e}")

    # 6) Report
    if errors:
        print("[VALIDATION FAILED]", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print("✅ Validation succeeded: all actions are well-formed.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    if len(sys.argv) != 2:
        print("Usage: validate_actions.py <path/to/actions.json>", file=sys.stderr)
        sys.exit(1)
    sys.exit(validate(sys.argv[1]))
