import json


def load_json_file(file_path: str) -> dict:
    """
    Load a JSON file and return its content as a dictionary.
    """
    with open(file_path) as file:
        data = json.load(file)
    return data
