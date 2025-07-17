# engine/interfaces/endpoint_api_handler.py

"""
Handles API endpoint and mid-stage API logic execution and transformation.

This module is responsible for:
- Handling API payloads for primary and mid-stage endpoints.
- Validating and preparing arguments for API calls.
- Logging and error handling.
- Transforming DP ID responses into UI-ready choices.
"""

from typing import Optional, Dict, Any
from monitoring.logger.logger import Logger
from config.api_config import PRIMARY_API_MAP, MID_STAGE_API_MAP
from engine.api_handlers.api_helpers import (
    extract_parameters,
    enrich_payload_with_type,
    transform_dp_ids_to_options,
    mtf_las_transform,
    advisor_change_transform

)

log = Logger()  # Initialize logger instance


def handle_primary_api(api_payloads: dict, user_data: dict, client_id: Optional[str], reason:Optional[str]) -> dict:
    """
    Handles execution of primary API endpoints.

    Args:
        api_payloads (dict): Payload data for the API.
        user_data (dict): Session or user data.
        client_id (str | None): Optional client ID fallback.

    Returns:
        dict: API response.
    """
    log.info(f"HANDLE PRIMARY API INITIATED")
    if not api_payloads:
        log.error("Missing API payloads data")
        return {"status": "Error", "action": "result", "message": "Data is not proper"}

    # Get API endpoint key from the payload
    endpoint = api_payloads.get("api_endpoint")
    log.info(f"{endpoint} - API ENDPOINT")
    if not endpoint:
        log.error("API endpoint key missing in payloads")
        return {"status": "Error", "action": "result", "message": "Data is not proper"}

    # Retrieve function and required parameters from primary map
    func_data = PRIMARY_API_MAP.get(endpoint)
    if not func_data:
        log.warning(f"No function mapping found for endpoint '{endpoint}'")
        return {"status": "Error", "action": "result", "message": "Functionality not supported"}

    try:
        # Unpack function and its expected parameters
        func, required_params = func_data
        # Extract only the required parameters from the payload
        final_args = extract_parameters(api_payloads, required_params)

        # If client_id is missing in extracted args, use the fallback client_id
        if not final_args.get("client_id") and client_id:
            final_args["client_id"] = client_id
        # Pass reason if available and not already present
        if reason is not None and not final_args.get("reason"):
            final_args["reason"] = reason

        log.debug(f"Calling endpoint '{endpoint}' with args: {final_args}")
        response = func(final_args)  # Call the actual function
        log.debug(f"Raw response from endpoint '{endpoint}': {response}")
        response["action"] = "result"  # Add default action for response routing

        log.info(f"API '{endpoint}' call successful")
        log.debug(f"Response: {response}")
        
        log.info(f"{response} - RESPONSE")
        return response

    except Exception as e:
        # Handle unexpected errors with trace logging
        log.critical(f"Error in endpoint '{endpoint}': {str(e)}", exc_info=True)
        return {"status": "Error", "action": "result", "message": "Server error, try again later."}


def handle_mid_stage_api(click_id: str, api_payloads: dict, client_id: Optional[str], reason: Optional[str] = None) -> dict:
    """
    Executes mid-stage API based on click ID logic and transforms the response.

    Args:
        click_id (str): Identifier for the mid-stage flow.
        api_payloads (dict): Payload from the user.
        client_id (str | None): Optional fallback.

    Returns:
        dict: Transformed response or error.
    """
    # Get the function and parameters associated with the click ID
    func_data = MID_STAGE_API_MAP.get(click_id)
    if not func_data:
        log.warning(f"No mapping found for mid-stage endpoint '{click_id}'")
        return {"status": "Error", "message": f"Invalid click ID '{click_id}'"}

    try:
        func, required_params = func_data
        # Extract only required fields from payload
        final_args = extract_parameters(api_payloads, required_params)
        # Enrich payload with any type/category metadata required for the mid-stage call
        final_args = enrich_payload_with_type(click_id, final_args)

        # Use fallback client_id if not already in arguments
        if not final_args.get("client_id") and client_id:
            final_args["client_id"] = client_id
        # Pass reason if available and not already present
        if reason is not None and not final_args.get("reason"):
            final_args["reason"] = reason

        log.debug(f"Calling mid-stage endpoint '{click_id}' with args: {final_args}")
        raw_response = func(final_args)
        raw_response = enrich_payload_with_type(click_id, raw_response)  # Call mid-stage API
        #raw_message = raw_response['Data'][0]['Message']
        raw_message = raw_response.get("Data")
        log.info(f"Raw response from mid-stage API '{click_id}': {raw_response}")
        # Transform raw DP ID response to a chatbot-friendly options list
        
        if isinstance(raw_message, list) and raw_message:
            log.info(f"{raw_message[0].get('Message', '').lower()}")    
            if raw_message[0].get("Message", "").lower() in ["yes", "no","YES", "NO","Yes", "No"]:
                return mtf_las_transform(raw_response)
            elif raw_message[0].get("Message", "").lower() in ["equity","commodity","both"]:
                return advisor_change_transform(raw_response)
            else:
                log.debug(f"Transforming API response: {raw_response}")
                return transform_dp_ids_to_options(raw_response, click_id)

    except Exception as e:
        log.critical(f"Error in mid-stage call '{click_id}': {str(e)}", exc_info=True)
        return {"status": "Error", "message": f"Execution failed for '{click_id}'"}
