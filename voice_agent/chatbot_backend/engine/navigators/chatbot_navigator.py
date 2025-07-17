# deterministic_engine/navigator/chatbot_navigator.py

from typing import Dict
from config.config import DEFAULT_NODE_CLIENT, DEFAULT_NODE_PARTNER, PARTNER_IDS, PARTNER_RQD_CLIENT_ID
from engine.session_managers.chatbot_session import ApiPayloadUploader
from engine.api_handlers.endpoint_api_handler import handle_primary_api, handle_mid_stage_api
from engine.navigators.special_handler_navigator import ChatbotSpecialNavigatorHandler
from monitoring.logger.logger import Logger

log = Logger()

class ChatbotNavigator:
    """
    Handles navigation logic for chatbot based on user interaction, session state, and flow definition.
    """

    def __init__(self, flow_data: Dict, session_manager, payload_session_manager):
        # Load the chatbot flow configuration and dependency managers
        self.flow_data = flow_data
        self.session_manager = session_manager
        self.payload_session_manager = payload_session_manager
        self.api_payload_uploader = ApiPayloadUploader
        self.chatbot_special_navigator_handler = ChatbotSpecialNavigatorHandler(payload_session_manager)

    def get_default_state_for_role(self, role: str) -> Dict:
        """
        Determines default chatbot node based on user role.
        """
        if role == "CLIENT":
            return self.get_flow_state(DEFAULT_NODE_CLIENT)
        elif role in PARTNER_IDS:
            return self.get_flow_state(DEFAULT_NODE_PARTNER)
        return {}  # No default state if role is unrecognized

    def get_flow_state(self, state_id: str) -> Dict:
        """
        Returns a flow state by ID with its corresponding node data.
        """
        state = self.flow_data.get(state_id, {}).copy()
        state["id"] = state_id
        return state

    def get_client_id_input_state(self, click_id: str) -> Dict:
        """
        Prompts partner user to enter a client ID when required by node.
        """
        log.info("Client id Ask...!")
        return {
            "action": "input",
            "id": f"client_id_{click_id}",
            "text": "Please enter the Client ID."
        }
    def get_reason_for_advisor_change(self, click_id: str) -> Dict:
        """
        Prompts user to enter a reason for advisor change when required by node.
        """
        log.info("Reason for Advisor Change Ask...!")
        return {
            "action": "input",
            "id": f"reason_{click_id}",
            "text": "Please enter the reason for advisor change."
        }

    def initialize(self, sess: str, uid: str, rl: str) -> Dict:
        """
        Initializes a new session with default state for given user role.
        """
        state = self.get_default_state_for_role(rl)
        self.session_manager.create_or_update_session(sess, uid, rl, state)
        return state

    def back(self, sess: str, rl: str) -> Dict:
        """
        Handles 'back' navigation by retrieving last state from history.
        """
        previous_state = self.session_manager.get_last_state(sess, self.flow_data)
        if previous_state:
            return previous_state
        return self.get_default_state_for_role(rl)

    def home(self, sess: str, uid: str, rl: str) -> Dict:
        """
        Resets the session to its default home state based on role.
        """
        state = self.get_default_state_for_role(rl)
        self.session_manager.create_or_update_session(sess, uid, rl, state)
        return state

    def navigate(self, sess: str, uid: str, rl: str, click_id: str, user_data: Dict) -> Dict:
        """
        Handles user click navigation and determines the next state or API response.
        """
        # Fetch current session data
        current = self.session_manager.get_session(sess)
        log.info(f"session data: {current}")

        # Build session-level API schema and update necessary payloads
        self.payload_session_manager.build_api_schema_for_session(sess, click_id)
        self.api_payload_uploader(
            self.payload_session_manager, sess, user_data, click_id, current["history_stack"]
        ).run_all_updates()

        # Ask for client ID if required for partner roles at specific nodes
        if rl in PARTNER_IDS and click_id in PARTNER_RQD_CLIENT_ID:
            return self.get_client_id_input_state(click_id)
        elif click_id in ["equity", "primary", "secondary", "both"]:
            return self.get_reason_for_advisor_change(click_id)
        # Handle custom click IDs via special dispatch logic
        click_id = self.chatbot_special_navigator_handler.dispatch_special_handlers(sess, user_data, click_id)
        if click_id is None:
            return {"Data": "Invalid client id input..!", 'action': 'result', 'Status': 'Failure'}
        log.info(f"CURRENT ID : {click_id}")
        # Proceed only if the click_id maps to a valid node
        if click_id in self.flow_data:
            next_state = self.get_flow_state(click_id)
            log.info(f"NEXT STATE : {next_state}")
            action = next_state.get("action")

            if action == "option":
                # Special handling for ledger_report: also call ledger_summary and fund_transfer_status and merge output
                if click_id == "ledger_report":
                    self.session_manager.create_or_update_session(sess, uid, rl, next_state)
                    payloads = self.payload_session_manager.get_api_paylods(sess)
                    client_id = self.payload_session_manager.get_client_id_for_partner(sess)
                    reason = self.payload_session_manager.get_reason_for_advisor_change(sess)
                    summary_result = handle_primary_api(
                        {**payloads, "api_endpoint": "ledger_summary"},
                        user_data,
                        client_id,
                        reason
                    )
                    fund_transfer_result = handle_primary_api(
                        {**payloads, "api_endpoint": "fund_transfer_link"},
                        user_data,
                        client_id,
                        reason
                    )
                    merged = dict(next_state)
                    merged["ledger_summary"] = summary_result
                    merged["fund_transfer_status"] = fund_transfer_result
                    return merged
                else:
                    self.session_manager.create_or_update_session(sess, uid, rl, next_state)
                    log.info(next_state)
                    return next_state
            elif action == "midapi":
                # Intermediate API call stage (e.g., dependent step)
                payloads = self.payload_session_manager.get_api_paylods(sess)
                client_id = self.payload_session_manager.get_client_id_for_partner(sess)
                reason = self.payload_session_manager.get_reason_for_advisor_change(sess)
                self.session_manager.create_or_update_session(sess, uid, rl, next_state)
                return handle_mid_stage_api(click_id, payloads, client_id, reason)
            elif action == "endapi":
                # Final API call step to return output to user
                log.info(f"END API CALL INITIATED")
                payloads = self.payload_session_manager.get_api_paylods(sess)

                client_id = self.payload_session_manager.get_client_id_for_partner(sess)
                reason = self.payload_session_manager.get_reason_for_advisor_change(sess)
                

                # log.info(client_id)
                
                return handle_primary_api(payloads, user_data, client_id, reason)

        # Handle invalid click or expired session scenario
        return {"Data": "Invalid data or expired session.", 'action': 'result', 'Status': 'Failure'}
