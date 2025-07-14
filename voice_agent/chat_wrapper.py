# chat_wrapper.py

import uuid
import httpx

BASE_URL = "http://localhost:8000"  # Update if running elsewhere

HEADERS = {
    "user-id": "NAGSYA5",
    "session-id": str(uuid.uuid4()),  # Dummy session ID for testing
    "client-id": "NAGSYA5",
    "role": "CLIENT",
    "token": str(uuid.uuid4()),  # Dummy token for testing
}

def generate_request_id():
    return str(uuid.uuid4())

async def run_chat(user_message: str) -> str:
    payload = {
        "input": {"text": user_message},
        "request_id": generate_request_id(),
        "type": "AGENTIC_FLOW"
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/chatbot/respond",
                json=payload,
                headers=HEADERS
            )
            response.raise_for_status()
            data = response.json()

            if data.get("success") and data["data"].get("message"):
                return data["data"]["message"]
            else:
                return "Sorry, I couldn't process that right now."
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 422:
            # Log the actual error details for debugging
            error_detail = e.response.text
            print(f"Validation error (422): {error_detail}")
            return f"Request validation failed. Please check the input format."
        return f"HTTP error {e.response.status_code}: {e.response.text}"
    except Exception as e:
        return f"Error reaching LangGraph backend: {e}"
