import json
from typing import Dict

def load_json_file(file_path: str) -> Dict:
    """
    Load a JSON file and return its content as a dictionary.
    """
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data