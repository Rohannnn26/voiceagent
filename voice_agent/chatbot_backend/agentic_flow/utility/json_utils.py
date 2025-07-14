

from monitoring.logger.logger import Logger

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

def read_and_pretty_print_json(file_name: str) -> str:
    """
    Reads a JSON file and returns a pretty-printed JSON string.

    Args:
        file_name (str): Name or relative path of the JSON file.

    Returns:
        str: Pretty-printed JSON string.
    """
    json_data = load_json_file(file_name)
    return json.dumps(json_data, indent=2)
