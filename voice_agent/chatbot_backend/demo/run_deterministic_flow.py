# demo.py
import json
from session.session_store import RedisSessionStore
from session.chatbot_session import ChatbotSessionManager
from data_loaders.json_loader import load_json
from config.config import JSON_FILE_PATH, REDIS_URL, REDIS_TTL_MINUTES, TEST_FILE_PATH
from core.chatbot_engine import ChatbotEngine

# Initialize the session store using Redis
store = RedisSessionStore(REDIS_URL, REDIS_TTL_MINUTES)

# Create a chatbot session manager with the Redis-backed store
session_manager = ChatbotSessionManager(store)

# Load chatbot flow definition from the JSON configuration file
json_data = load_json(JSON_FILE_PATH)

# Instantiate the chatbot engine with the loaded data and session manager
engine = ChatbotEngine(json_data, session_manager)

def run_tests_from_file(file_path: str):
    """
    Load test cases from a file and simulate sessions for each user.
    """
    test_cases = load_json(file_path)

    for case in test_cases:
        user_payload = {
                    "user_id": case["user_id"],
                    "session_id": case["session_id"],
                    "client_id": "client_test",
                    "role": "user",
                    "auth_token": "test_token",
                    "request_type": "deterministic",  # <--- use this!
                    "interaction": {
                        "click_id": "home",
                        "input_text": None,
                        "metadata": {
                            "timestamp": "2024-04-24T12:00:00Z",
                            "ui_version": "v2.1.0"
                        }
                    }
                }

        print(f"\n--- Starting session for {user['user_id']} ({user['session_id']}) ---\n")
        # print("Init:", engine.handle_input(user))
        print("\n")

        for step in case["steps"]:
            user["interaction"]["click_id"] = step
            response = engine.handle_input(user)
            print(f"{step} ->", response)
            print("\n")
        print(f"\n--- End of session {user['session_id']} ---\n")


if __name__ == "__main__":
    run_tests_from_file(TEST_FILE_PATH)