# modules/data_loader.py

import json
import os
from typing import Dict, Any

def load_json(file_path: str) -> Dict[str, Any]:
    """
    Load a JSON file from disk and return its contents as a dictionary.

    Args:
        file_path (str): Full path to the JSON file.

    Returns:
        dict: Parsed JSON content if file exists and is valid, otherwise an empty dict.
    """
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)  # Load and parse JSON file
        except Exception as e:
            print(f"Error loading JSON file: {e}")
    else:
        print(f"JSON file not found at path: {file_path}")
    return {}  # Return empty dict as fallback


def handle_user_input(data_dict: Dict[str, Any], user_inputs: Dict[str, str]) -> Dict[str, Any]:
    """
    Retrieve a specific flow/state entry from the JSON based on a user click/input.

    Args:
        data_dict (dict): The full JSON dataset containing all flow states.
        user_inputs (dict): User data that includes an 'id' key representing a button click.

    Returns:
        dict: Corresponding flow entry if found; otherwise, an error message.
    """
    button_id = user_inputs.get('id')

    # Check if the button ID is present in the loaded JSON
    if button_id not in data_dict:
        return {"error": f"Invalid id: {button_id}"}

    # Fetch and return the JSON node for the button ID
    return data_dict[button_id]
