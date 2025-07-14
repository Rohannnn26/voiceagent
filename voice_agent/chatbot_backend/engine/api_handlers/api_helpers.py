# engine/interfaces/api_helpers.py

"""
Utility helpers for API parameter preparation and response transformation.

This module provides:
- Safe parameter extraction from payloads.
- Payload enrichment with contextual information.
- Transformation of raw API responses into frontend-ready choice formats.
"""

from typing import Dict, Any
from monitoring.logger.logger import Logger
import json

log = Logger()


def extract_parameters(payload: Dict[str, Any], required_keys: list) -> Dict[str, Any]:
    """
    Extracts a subset of parameters from the payload based on required keys.

    Args:
        payload (dict): Incoming API payload.
        required_keys (list): Keys expected by the API handler.

    Returns:
        dict: A dictionary with only the required parameters.
    """
    return {key: payload.get(key) for key in required_keys}


def enrich_payload_with_type(click_id: str, args: dict) -> dict:
    """
    Enriches the argument payload by injecting a `type` field based on the click ID.
    This is typically used for flows like MTF or LAS.

    Args:
        click_id (str): Identifier representing the source or context.
        args (dict): Arguments to be passed to the mid-stage API.

    Returns:
        dict: Modified argument dictionary with type enrichment.
    """
    if click_id in {"MTF","Equity","Commodity"}:
        args["type"] = click_id
        
    return args


def transform_dp_ids_to_options(response: Dict[str, Any], click_id:str) -> Dict[str, Any]:
    """
    Transforms a comma-separated 'dpId' string in the API response into a structured list of choices.

    Args:
        response (dict): Raw API response expected to contain a `dpId` key.

    Returns:
        dict: Structured response with available choices or error message.
    """
    if not isinstance(response, dict):
        log.error("Invalid input: Expected dict in dpId transformer")
        return {"status": "Error", "message": "Invalid response format"}

    dp_id_string = response.get("Data", [])
    
    if not dp_id_string:
        log.warning("Missing 'dpId' in API response")
        return {"status": "Error", "message": "No DPId found in response"}

    try:
        dp_ids = [item['DPID'] for item in dp_id_string]
        log.debug(f"Extracted DP IDs: {dp_ids}")

        choices = [{"id": "dp_ids_cmr" if click_id == "digi_cmr" else "dp_ids", "text": dp_id} for dp_id in dp_ids]
        return {
            "action": "option",
            "response_text": "Here are the list of DP ID's",
            "available_choices": choices,
        }

    except Exception as e:
        log.critical(f"Exception during DP ID transformation: {str(e)}", exc_info=True)
        return {"status": "Error", "message": "Failed to transform dpId data"}



def mtf_las_transform(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforms a comma-separated 'message' string in the API response into a structured list of choices.

    Args:
        response (dict): Raw API response expected to contain a `message` key.

    Returns:
        dict: Structured response with available choices or error message.
    """
    if not isinstance(response, dict):
        log.error("Invalid input: Expected yes or no in message")
        return {"status": "Error", "message": "Invalid response format"}

    mtf_las_msg = response['Data'][0]['Message']
    log.info(f"API Helper: {mtf_las_msg}")
    #mtf_las_type = response.get("type")
    
    if not mtf_las_msg:
        log.warning("Missing 'mtf_message' in API response")
        return {"status": "Error", "message": "No mts_msg found in response"}

    try:
               
        #log.debug(f"Extracted DP IDs: {dp_ids}")
        if mtf_las_msg.lower() == "no":
            return {
            "message": "You are not MTF client",
        }
        elif mtf_las_msg.lower() == "yes":
            log.info(f"API Helper: {mtf_las_msg.lower()}")
            
            return {
            "action": "option",
            "message": "",
            "available_choices": [
        {
          "id": "Voucher",
          "text": "Voucher Date Wise"
        }, 
        {
          "id": "Effective",
          "text": "Effective Date wise"
        }
      ],
        }
        else:
            log.error("Invalid message value: Expected 'yes' or 'no'")
            return {"status": "Error", "message": "Invalid message value"}

    except Exception as e:
        log.critical(f"Exception during mtf_msg transformation: {str(e)}", exc_info=True)
        return {"status": "Error", "message": "Failed to transform mtf_msg data"}
    
def advisor_change_transform(response: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(response, dict):
        log.error("Invalid input: Expected Equity or Commodity in message")
        return {"status": "Error", "message": "Invalid response format"}

    mtf_las_msg = response.get("Data",{}).get("Message",{})
    #mtf_las_type = response.get("type")
    
    if not mtf_las_msg:
        log.warning("Missing 'mtf_message' in API response")
        return {"status": "Error", "message": "No mts_msg found in response"}