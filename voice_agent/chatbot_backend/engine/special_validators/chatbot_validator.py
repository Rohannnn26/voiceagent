# deterministic_engine/validator/chatbot_validator.py

from integrations.external_api_wrapper import valid_clientcode
from monitoring.logger.logger import Logger

# Initialize custom logger for validation logs
log = Logger()

class ChatbotValidator:
    """
    Handles validation of client codes by invoking external API checks.
    """

    def verify_client_code(self, user_data: dict) -> bool:
        """
        Validates the client code extracted from user interaction.

        Args:
            user_data (dict): Dictionary containing session and user information.

        Returns:
            bool: True if the client code is valid, False otherwise.
        """
        # Extract required information from user input
        session_id = user_data["session_id"]
        user_id = user_data["user_id"]
        role = user_data["role"]
        token = user_data["token"]
        client_id = user_data.get("interaction", {}).get("input", {}).get("text")

        # Prepare parameters for external validation API
        params = {
            "session_id": session_id,
            "token": token,
            "user_id": user_id,
            "client_id": client_id,
            "role": role
        }
        log.info(f"CLIENT API PARAMS - {params}")

        # Log parameters before API call for traceability
        log.debug(f"Client validation params: {params}!")

        # Call the external service to validate client code
        response = valid_clientcode(params)

        # Check if client code is valid and log accordingly
        if response["Data"][0]["Message"] == "Valid Client":
            log.info("Client code is Valid..!")
            return True

        # Log invalid client response
        log.info("Client code is Invalid..!")
        log.debug(f"Client validation response : {response}!")
        return False
