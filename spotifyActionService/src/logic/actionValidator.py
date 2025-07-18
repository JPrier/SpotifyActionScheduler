#!/usr/bin/env python3
import sys
import json
from pathlib import Path

from accessor.configLoader import load_json_file
from jsonschema import Draft202012Validator

SCHEMA_PATH = Path(__file__).resolve().parents[3] / "actions.schema.json"

with open(SCHEMA_PATH) as f:
    _SCHEMA = json.load(f)
_VALIDATOR = Draft202012Validator(_SCHEMA)

# Return codes used throughout the application
VALIDATION_SUCCESS = 0
VALIDATION_FAILED = 1


def validate(filepath: str) -> int:
    # 1) Load the JSON (reports parse errors)
    try:
        data = load_json_file(filepath)
    except Exception as e:
        print(f"[ERROR] Unable to load JSON: {e}", file=sys.stderr)
        return VALIDATION_FAILED
    
    return validate_data(data)
    
def validate_data(data: dict) -> int:
    """Validate the given data against the actions JSON schema."""

    if "actions" not in data or not isinstance(data["actions"], list):
        print("[ERROR] Top-level 'actions' key missing or not a list.", file=sys.stderr)
        return VALIDATION_FAILED

    errors = sorted(_VALIDATOR.iter_errors(data), key=lambda e: e.path)
    if errors:
        print("[VALIDATION FAILED]", file=sys.stderr)
        for err in errors:
            path = "".join(
                f"[{p}]" if isinstance(p, int) else f".{p}" for p in err.absolute_path
            )
            if path.startswith("."):
                path = path[1:]
            print(f"  - {path or '<root>'}: {err.message}", file=sys.stderr)
        return VALIDATION_FAILED

    print("✅ Validation succeeded: all actions are well-formed.")
    return VALIDATION_SUCCESS


if __name__ == "__main__":  # pragma: no cover
    if len(sys.argv) != 2:
        print("Usage: validate_actions.py <path/to/actions.json>", file=sys.stderr)
        sys.exit(1)
    sys.exit(validate(sys.argv[1]))
