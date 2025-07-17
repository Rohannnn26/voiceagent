from typing import Dict, Optional
from engine.special_validators.chatbot_validator import ChatbotValidator
from monitoring.logger.logger import Logger
from agentic_flow.utility.text_extract_utils import extract_client_id_from_message
log = Logger()

class ChatbotSpecialNavigatorHandler:
    def __init__(self, payload_session_manager):
        # Initialize the validator and store the payload session manager
        self.validator = ChatbotValidator()
        self.payload_session_manager = payload_session_manager

    def _handle_client_id_input(self, session_id: str, user_data: Dict, click_id: str) -> Optional[str]:
        """
        Handles the input flow when a client ID is required from a partner user.

        Validates the client ID entered by the user using ChatbotValidator.
        If valid, stores the client ID in the payload session and returns the
        actual click ID to resume normal navigation.

        Args:
            session_id (str): Unique session identifier.
            user_data (Dict): User metadata and interaction input.
            click_id (str): Current click ID (e.g., "client_id_node12").

        Returns:
            Optional[str]: The actual click ID to navigate to if validation passes,
                           else None if validation fails.
        """
        if self.validator.verify_client_code(user_data):
            # Extract valid client ID from user input
            text = user_data.get("interaction", {}).get("input", {}).get("text")
            log.info(f"Extracting client ID from message before llm: {text}")
            client_id = extract_client_id_from_message(text)
            log.info(f"Extracting client ID from message after llm: {client_id}")
           
            
            # Remove the "client_id_" prefix to get the real click ID
            actual_click_id = click_id.removeprefix("client_id_")
            # Store the validated client ID in the session
            self.payload_session_manager.add_client_id_for_partner(session_id, client_id)
            return actual_click_id  # Proceed with navigation
        return None  # Validation failed; stop navigation

    def handle_reason_for_advisor_change(self, session_id: str, user_data: Dict, click_id: str) -> Optional[str]:

        """
        Handles the input flow when a reason for advisor change is required.

        Validates the reason entered by the user. If valid, stores the reason
        in the payload session and returns the actual click ID to resume normal navigation.

        Args:
            session_id (str): Unique session identifier.
            user_data (Dict): User metadata and interaction input.
            click_id (str): Current click ID (e.g., "reason_node12").

        Returns:
            Optional[str]: The actual click ID to navigate to if validation passes,
                           else None if validation fails.
        """
        # Extract reason from user input
        reason = user_data.get("interaction", {}).get("input", {}).get("text")
        
        # Remove the "reason_" prefix to get the real click ID
        actual_click_id = click_id.removeprefix("reason_")
        
        # Store the reason in the session
        self.payload_session_manager.add_reason_for_advisor_change(session_id, reason)
        
        return actual_click_id
    def dispatch_special_handlers(self, session_id: str, user_data: Dict, click_id: str) -> Optional[str]:
        """
        Dispatches special click handlers based on click ID prefix.

        This allows dynamic routing to handler functions when special input
        types (like client ID) are needed before proceeding.

        Args:
            session_id (str): Current session ID.
            user_data (Dict): User interaction and metadata.
            click_id (str): Click ID from the chatbot flow.

        Returns:
            Optional[str]: Modified click ID after handling or None if validation fails.
        """
        # Dictionary of special click_id prefixes and corresponding handler methods
        special_handlers = {
            "client_id_": self._handle_client_id_input,
            "reason_": self.handle_reason_for_advisor_change,
            # Future handlers can be added here
            # e.g., "admin_id_": self._handle_admin_id_input,
        }

        # Match the click ID prefix with a registered handler
        for key_prefix, handler in special_handlers.items():
            if click_id.startswith(key_prefix):
                # Route to the corresponding handler
                return handler(session_id, user_data, click_id)

        return click_id  # No special handler matched; return click_id unchanged
