

from monitoring.logger.logger import Logger
from config.config import BASE_URL_CONFIG , env

import os
import json
from datetime import datetime

log = Logger()

today_date = datetime.today().strftime("%m/%d/%Y")

def get_indian_financial_year() -> tuple:
    """
    Returns the start and end dates of the current Indian financial year.
    The Indian financial year runs from April 1st to March 31st of the following year.
    
    Returns:
        tuple: (start_date, end_date) in "YYYY-MM-DD" format
            - start_date: April 1st of current or previous year
            - end_date: March 31st of next or current year
    """
    current_date = datetime.today()
    current_year = current_date.year
    current_month = current_date.month
    
    # If current month is January, February, or March, we're in the latter part of the financial year
    if current_month <= 3:  # January to March
        fy_start_year = current_year - 1
        fy_end_year = current_year
    else:  # April to December
        fy_start_year = current_year
        fy_end_year = current_year + 1
        
    start_date = f"04/01/{fy_start_year}"
    end_date = f"03/31/{fy_end_year}"
    
    return (start_date, end_date)
    

def load_json_file(file_name: str) -> dict:
    """
    Loads and parses a JSON file from the current working directory.

    Args:
        file_name (str): Name or relative path to the JSON file.

    Returns:
        dict: Parsed JSON content.
    """
    root_folder = os.getcwd()
    file_path = os.path.join(root_folder, file_name)
    log.info(f"Loading JSON file from path: {file_path}")
    with open(file_path, 'r') as f:
        return json.load(f)

def update_system_param_mapper(file_name: str) -> dict:
    """
    Reads the system parameters mapper JSON file and returns the parsed content
    with updated keys prefixed by the base URL.

    Args:
        file_name (str): Name or relative path of the JSON file.

    Returns:
        dict: Updated JSON content.
    """
    data = load_json_file(file_name)
    log.info(f"System parameters mapper loaded from {file_name}")
    if not data:
        log.error(f"Failed to load system parameters mapper from {file_name}")
        return {}

    updated_data = {}
    for key, value in data.items():
        new_key = f"{BASE_URL_CONFIG.rstrip('/')}/{key.lstrip('/')}"
        updated_data[new_key] = value

    log.info("System parameters mapper updated with base URL.")
    return updated_data


def update_paths_with_base_url(file_name: str):
    """
    Reads the OpenAPI JSON file, updates path keys by prefixing them with base_url + '/',
    and returns the modified JSON dict.

    If 'paths' key doesn't exist, returns the original JSON unchanged.
    """
    data = load_json_file(file_name)
    
    if 'paths' not in data:
        log.info("'paths' key not found in JSON; returning original data unchanged.")
        return data

    original_paths = data['paths']
    updated_paths = {}
    
    for key, value in original_paths.items():
        new_key = f"{BASE_URL_CONFIG.rstrip('/')}/{key.lstrip('/')}"
        updated_paths[new_key] = value
    
    data['paths'] = updated_paths
    return data

def read_and_pretty_print_json(file_name: str) -> str:
    """
    Reads a JSON file and returns a pretty-printed JSON string.

    Args:
        file_name (str): Name or relative path of the JSON file.

    Returns:
        str: Pretty-printed JSON string.
    """
    # json_data = load_json_file(file_name)
    json_data = update_paths_with_base_url(file_name)
    return json.dumps(json_data, indent=2)
