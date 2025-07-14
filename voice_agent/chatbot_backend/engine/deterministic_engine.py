from typing import Dict
from engine.session_managers.chatbot_session import ChatbotSessionManager, PayloadSessionManager
from engine.navigators.chatbot_navigator import ChatbotNavigator

from monitoring.logger.logger import Logger
log = Logger()

class ChatbotEngine:
    """
    Core engine to control the chatbot's session, navigation, and user input handling.
    """

    def __init__(self, json_data: Dict, session_manager: ChatbotSessionManager, payload_session_manager: PayloadSessionManager):
        # Initialize chatbot engine with flow data and session managers
        self.flow_data = json_data
        self.session_manager = session_manager
        self.payload_session_manager = payload_session_manager
        # Navigator handles conversation flow based on user interaction
        self.navigator = ChatbotNavigator(json_data, session_manager, payload_session_manager)

    def handle_input(self, user_data: Dict) -> Dict:
        """
        Main entry point to handle user input and determine navigation flow.
        """
        session_id = user_data["session_id"]
        user_id = user_data["user_id"]
        role = user_data["role"]
        click_id = user_data["interaction"]["input"]["id"]
        # Start a new session if one does not exist
        if not self.session_manager.get_session(session_id):
            return self.navigator.initialize(session_id, user_id, role)

        # Handle 'back' navigation
        if click_id == "back":
            return self.navigator.back(session_id, role)

        # Handle 'home' or 'initial' navigation reset
        if click_id in ["home", "initial"]:
            return self.navigator.home(session_id, user_id, role)

        # Proceed with normal navigation flow
        return self.navigator.navigate(session_id, user_id, role, click_id, user_data)
