# engine/session/chatbot_session.py

from datetime import datetime
from typing import Dict, Optional
from engine.session_managers.session_store import RedisSessionStore
from config.api_config import PRIMARY_API_MAP
from integrations.date_utils import date_range
from monitoring.logger.logger import Logger
log = Logger()

class ChatbotSessionManager:
    """
    Manages user session lifecycle for the chatbot using a Redis-based store.
    
    Tracks the current state, role, history (for back navigation), and timestamps.
    """

    def __init__(self, store: RedisSessionStore):
        """
        Initialize the session manager with a persistent session store.

        Args:
            store (RedisSessionStore): A Redis-based session storage backend.
        """
        self.store = store

    def create_or_update_session(self, session_id: str, user_id: str, role: str, input_params: Dict):
        """
        Create a new session or update an existing one with the current flow state.

        Args:
            session_id (str): Unique session identifier.
            user_id (str): User's ID.
            role (str): User's role (e.g., admin, guest).
            input_params (Dict): Current state node with metadata.

        Returns:
            Dict: Success message with session ID.
        """
        now = datetime.utcnow().isoformat()  # Current UTC timestamp
        existing_session = self.store.load(session_id)  # Load session if it exists

        history_stack = []
        current_state_id = None
        new_state_id = input_params.get("id")  # New state we are transitioning to

        if existing_session:
            history_stack = existing_session.get("history_stack", [])
            current_input_params = existing_session.get("input_params", {})
            current_state_id = current_input_params.get("id")

            # Avoid appending the same state repeatedly
            if current_state_id and current_state_id != new_state_id:
                history_stack.append(current_state_id)

        # Updated session structure to persist
        session_data = {
            "user_id": user_id,
            "role": role,
            "input_params": input_params,
            "last_updated": now,
            "history_stack": history_stack
        }

        self.store.save(session_id, session_data)
        return {"message": "Session updated", "session_id": session_id}

    def get_session(self, session_id: str) -> Optional[Dict]:
        """
        Retrieve the current session for a given session ID.

        Args:
            session_id (str): The session identifier.

        Returns:
            Optional[Dict]: Session data if it exists, else None.
        """
        return self.store.load(session_id)

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session from the store.

        Args:
            session_id (str): The session identifier.

        Returns:
            bool: True if the session existed and was deleted, False otherwise.
        """
        exists = bool(self.store.load(session_id))
        if exists:
            self.store.delete(session_id)
        return exists

    def list_all_sessions(self) -> list:
        """
        List all active session keys.

        Returns:
            list: A list of session IDs (keys) stored in Redis.
        """
        return self.store.list_keys()

    def get_last_state(self, session_id: str, flow_data: Dict) -> Optional[Dict]:
        """
        Navigate backward by popping the last state from the history stack.

        Args:
            session_id (str): The session identifier.
            flow_data (Dict): The full chatbot flow to look up state details.

        Returns:
            Optional[Dict]: The previous state if history exists, otherwise None.
        """
        session = self.store.load(session_id)

        if not session:
            return None

        history_stack = session.get("history_stack", [])
        if not history_stack:
            return None

        last_state_id = history_stack.pop()  # Remove and get the last visited state
        session["history_stack"] = history_stack
        session["input_params"] = flow_data.get(last_state_id, {})  # Restore old state data
        session["last_updated"] = datetime.utcnow().isoformat()

        self.store.save(session_id, session)  # Save updated session with shortened history
        return flow_data.get(last_state_id)

# Creating the payload schema and what all parameter are required
class PayloadSessionManager:
    def __init__(self, store: RedisSessionStore):
        """
        Initialize the session manager with a persistent session store.

        Args:
            store (RedisSessionStore): A Redis-based session storage backend.
        """
        self.store = store
        self.endpoint_mapping = PRIMARY_API_MAP
    
    def add_client_id_for_partner(self, session_id:str, client_id:str) -> None:
        redis_key = f"{session_id}_client_id"
        # Construct the user_id data dict
        client_id_session_data = {
            "client_id": client_id,
            "last_updated": datetime.utcnow().isoformat()
        }
        log.info(f"client id is added: {client_id}")
        # Save the updated payload under a namespaced Redis key
        self.store.save(redis_key, client_id_session_data)

    def get_client_id_for_partner(self, session_id: str) -> Optional[str]:
        redis_key = f"{session_id}_client_id"
        log.info(redis_key)
        client_id_data = self.store.load(redis_key)
        log.info(client_id_data)
        log.info(f"Client id fetched from Redis: {client_id_data}")

        if client_id_data and "client_id" in client_id_data:
            return client_id_data["client_id"]
        else:
            log.error(f"Client ID not found in Redis for session: {session_id}")
            return None

    def build_api_schema_for_session(self, session_id: str, click_id: str) -> None:
        """
        Initializes the API schema structure for a session-specific payload key if the click_id is valid and mapped.
        
        This builds a dictionary of required payload keys, sets the endpoint, and stores it in Redis under a key 
        formatted as '{session_id}_api_payload'.

        Args:
            session_id (str): Unique identifier for the session.
            click_id (str): Identifier for the node/endpoint to determine schema.
        """
        if click_id not in self.endpoint_mapping:
            # If there's no schema required for this click_id, simply return.
            return

        redis_key = f"{session_id}_api_payload"

        # Get function and required schema fields from mapping
        _, required_keys = self.endpoint_mapping[click_id]

        # Build a fresh payload structure
        api_payloads = {key: None for key in required_keys}
        api_payloads["api_endpoint"] = click_id

        # Construct the full session data dict
        payloads_session_data = {
            "api_payloads": api_payloads,
            "last_updated": datetime.utcnow().isoformat()
        }

        # Save the updated payload under a namespaced Redis key
        self.store.save(redis_key, payloads_session_data)

    def add_or_update_api_paylods(self, session_id: str, param_key: str, value) -> bool:
        """
        Update a specific key under 'api_payloads' in a session if all of the following exist:
        - 'payloads_session_data' is found
        - 'api_payloads' is present
        - 'api_endpoint' is set in 'api_payloads'
        - 'param_key' already exists in 'api_payloads'

        Args:
            session_id (str): Session identifier.
            param_key (str): The parameter key to update.
            value: The value to assign to the parameter.

        Returns:
            bool: True if the key was updated, False otherwise (including missing structures).
        """
        redis_key = f"{session_id}_api_payload"
        payloads_session_data = self.store.load(redis_key)
        if not payloads_session_data:
            return False

        api_payloads = payloads_session_data.get("api_payloads")
        if not api_payloads or "api_endpoint" not in api_payloads:
            return False

        if param_key not in api_payloads:
            return False

        # Update and persist
        payloads_session_data["api_payloads"][param_key] = value
        payloads_session_data["last_updated"] = datetime.utcnow().isoformat()
        self.store.save(redis_key, payloads_session_data)
        return True

    def get_api_paylods(self, session_id: str) -> Dict:
        """
        Fetch current api_payloads structure.
        """
        redis_key = f"{session_id}_api_payload"
        payloads_session_data = self.store.load(redis_key)
        log.info(f"get_api_paylods: {payloads_session_data}")
        # log.info(f"API PAYLOAD : {payloads_session_data.get("api_payloads", {})} ")
        return payloads_session_data.get("api_payloads", {}) if payloads_session_data else {}

# uploading the API payload
class ApiPayloadUploader:
    def __init__(self, manager, session_id: str, user_data: Dict, click_id: str, history_stack: Optional[list] = None):
        """
        Initialize with manager instance, session ID, user data, and click_id.
        """
        self.manager = manager
        self.session_id = session_id
        self.user_data = user_data
        self.click_id = click_id
        self.history_stack = history_stack

    def update_header(self):
        """
        Update standard header fields in api_payloads.
        """
        keys = ["user_id", "client_id", "role", "token", "session_id"]
        for key in keys:
            self.manager.add_or_update_api_paylods(self.session_id, key, self.user_data.get(key))
        log.info(f"Updated user data: {self.user_data}")

    def update_segment(self):
        """
        Update the segment field in api_payloads based on click_id.
        """
        if self.click_id == "Combine":
            self.manager.add_or_update_api_paylods(self.session_id, "exchange_seg", "COMBINE")
            log.info(f"Segment type for click id: {self.click_id} is 'Combine'.")
        elif self.click_id == "MTF":
            self.manager.add_or_update_api_paylods(self.session_id, "exchange_seg", "MTF")
            log.info(f"Segment type for click id: {self.click_id} is 'MTF'.")

    def update_date_range(self):
        """
        Update from_date and to_date based on click_id preset.
        """
        if self.click_id in {"3_month", "6_month", "current_fy", "previous_fy","current_fy_itr","previous_fy_itr","current_fy_stt_ctt","previous_fy_stt_ctt","current_margin_shortage","previous_margin_shortage"}:
            from_date, to_date = date_range(self.click_id)
            self.manager.add_or_update_api_paylods(self.session_id, "from_date", from_date)
            self.manager.add_or_update_api_paylods(self.session_id, "to_date", to_date)
    
    def dis_drf_status(self):
        """Update dis_drf_status based on click_id."""

        if self.click_id == "drfStatus":
            self.manager.add_or_update_api_paylods(self.session_id, "request_type", "drfStatus")
            self.manager.add_or_update_api_paylods(self.session_id, "ref_no", "2")
            log.info(f"segment-type for click id: {self.click_id} is 'drfStatus'.")
        elif self.click_id == "disStatus":
            self.manager.add_or_update_api_paylods(self.session_id, "request_type", "disStatus")
            self.manager.add_or_update_api_paylods(self.session_id, "ref_no", "1")
            log.info(f"segment-type for click id: {self.click_id} is 'disStatus'.")
            
    def update_return_type(self):
        """
        Update return_type if click_id is Email or Link.
        """
        if self.click_id in {"Email", "Link"}:
            self.manager.add_or_update_api_paylods(self.session_id, "return_type", self.click_id)
            log.info(f"Return type: {self.click_id}")

    def update_statement_type(self):
        """
        Update statement_type based on click_id.
        """
        if self.click_id == "dp_holdings":
            self.manager.add_or_update_api_paylods(self.session_id, "statement_type", "H")
            log.info(f"Statement type for click id: {self.click_id} is 'H'.")
        elif self.click_id == "transaction_statement":
            self.manager.add_or_update_api_paylods(self.session_id, "statement_type", "T")
            log.info(f"Statement type for click id: {self.click_id} is 'T'.")
    
    def add_dp_id(self): 
        payloads_session_data = self.manager.get_api_paylods (self.session_id)   
        if "dp_id" in payloads_session_data and "dp_ids" == self.click_id:
            dp_id = self.user_data.get("interaction", {}).get("input", {}).get("text")
            if not dp_id:
                log.error("Unable to get the DP ID from user!")
            self.manager.add_or_update_api_paylods(self.session_id, "dp_id", dp_id)
            log.info(f"'dp_id' key exists. Setting dp_id to: {dp_id}")


    def emod_type(self):
        """Update emod_type based on click_id."""

        if self.click_id == "dormant_status":
            self.manager.add_or_update_api_paylods(self.session_id, "type", "DOR")
            log.info(f"E-type for click id: {self.click_id} is 'DOR'.")
        if self.click_id in ["email_and_mobile","address_online","bank_online","nominee"]:
            self.manager.add_or_update_api_paylods(self.session_id, "type", "Emod")
            log.info(f"E-type for click id: {self.click_id} is 'Emod'.")

    def date_type(self):
        """Update date_type based on click_id."""

        if self.click_id == "Voucher":
            self.manager.add_or_update_api_paylods(self.session_id, "date_type", "VOUCHER")
            log.info(f"date type for click id: {self.click_id} is 'VOUCHER'.")
        elif self.click_id == "Effective":
            self.manager.add_or_update_api_paylods(self.session_id, "date_type", 'EFFECTIVE')
            log.info(f"date type for click id: {self.click_id} is 'EFFECTIVE'.")

    def account_opening_partner(self):
        """Update emod_type based on click_id."""

        click_id_mapping = {
            "individuals_acc_online": ("ind_online", "IND_acc_onl"),
            "individuals_acc_physical_checklist": ("ind_physical_checklist", "IND_acc_phy"),
            "individuals_acc_physical_sample_form": ("ind_physical_form", "IND_acc_phy"),
            "huf_acc_checklist": ("huf_checklist", "huf_check"),
            "huf_acc_physical_checklist": ("huf_sample", "huf_sample_form"),
            "nri_checklist": ("nri_checklist", "nri_check"),
            "nri_sample_form": ("nri_sample", "nri_sample_form"),
            "partnership_checklist": ("partnership_checklist", "partnership_check"),
            "partnership_sample_form": ("partnership_sample", "partnership_sample_form"),
            "corporate_checklist": ("corporate_checklist", "corporate_check"),
            "corporate_sample_form": ("corporate_sample", "corporate_sample_form"),
            "registered_trust_checklist": ("registered_trust_checklist", "registered_trust_check"),
            "registered_trust_sample_form": ("registered_trust_sample", "registered_trust_sample_form"),
            "non_registered_trust_checklist": ("non_registered_trust_checklist", "non_registered_trust_check"),
            "non_registered_trust_sample_form": ("non_registered_trust_sample", "non_registered_trust_sample_form"),
            "reactivation_checklist": ("reactivation_checklist", "reactivation_check"),
            "reactivation_sample_form": ("reactivation_sample", "reactivation_sample_form"),
            "reactivation_dormant": ("reactivation_dormant", "reactivation_dormant"),
            "new_form_request_acc": ("new_form_request", "new_form_request"),
        }

        mo_kyc_click_id = {
            "individuals_acc_physical_ppt", "nri_ppt", "partnership_ppt", "corporate_ppt", "registered_trust_ppt"
        }

        if self.click_id in mo_kyc_click_id:
            account_type, log_label = "ind_physical_document", "IND_acc_phy"
        elif self.click_id in click_id_mapping:
            account_type, log_label = click_id_mapping[self.click_id]
        else:
            log.warning(f"Unknown click_id: {self.click_id}")
            return

        self.manager.add_or_update_api_paylods(self.session_id, "account_type", account_type)
        log.info(f"Acc opening for click id: {self.click_id} is '{log_label}'.")



    def order_type(self):
        """
        Update the segment field in api_payloads based on click_id.
        """
        order_map = {
            "sip": "SIP",
            "xsip": "XSIP",
            "isip": "ISIP",
            "fp": "FP",
            "mn": "MN",
        }

        if self.click_id in order_map:
            order_value = order_map[self.click_id]
            self.manager.add_or_update_api_paylods(self.session_id, "order_type", order_value)
            log.info(f"Segment type for click id: {self.click_id} is '{order_value}'.")
        else:
            log.info(f"No segment mapping found for click id: {self.click_id}")

    def segment_type(self):
        """Update emod_type based on click_id."""

        if self.click_id == "equity":
            self.manager.add_or_update_api_paylods(self.session_id, "segmenttype", "Equity")
            log.info(f"segment-type for click id: {self.click_id} is 'DOR'.")
        elif self.click_id == "commodity":
            self.manager.add_or_update_api_paylods(self.session_id, "segmenttype", "Commodity")
            log.info(f"segment-type for click id: {self.click_id} is 'Commodity'.")



    def run_all_updates(self):
        """
        Run all relevant update methods with no return value.
        """
        self.update_header()
        self.update_segment()
        self.update_date_range()
        self.update_return_type()
        self.update_statement_type()
        self.dis_drf_status()
        self.add_dp_id()
        self.order_type()
        self.emod_type()
        self.account_opening_partner()
        self.segment_type()
        self.date_type()
