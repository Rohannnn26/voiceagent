# app/api/v1/chatbot_routes.py

from fastapi import APIRouter, Header, HTTPException
from app.schemas.request_models import Interaction, Payload, InteractionV2
from app.services.chatbot_service import get_chatbot_response
# from integrations.external_api_wrapper import get_register_token
from monitoring.logger.logger import Logger

# Initialize logger
log = Logger()

router = APIRouter()

@router.post("/chatbot/respond")
def chatbot_respond(
    interaction: InteractionV2,  # only the body
    user_id: str = Header(..., alias="user-id"),
    session_id: str = Header(..., alias="session-id"),
    client_id: str = Header(..., alias="client-id"),
    role: str = Header(..., alias="role"),
    # auth_token: str = Header(None, alias="auth-token"),
    token: str = Header(None, alias="token"),
    # request_type: str = Header(..., alias="request-type")
):
    try:
        # register_params = {"user_id": user_id, "token": token}
        # log.info(f"Registering user with params: {register_params}")
        # # Register the user and get the response
        # registration_response = get_register_token(register_params)

        # if not all(register_params.values()) or not registration_response :
        #     log.error(f"Register Params: {register_params}")
        #     return {
        #         "success": False,
        #         "data": {
        #             "Status": "Failure",
        #             "Data": "Missing required registration parameters or registration response is empty. Please check your request."
        #         }
        #     }
        
        # if registration_response.get("Status") != "Success" or registration_response.get("error"):
        #     log.error(f"Registration failed: {registration_response}")
        #     return {
        #         "success": False,
        #         "data": {
        #             "Status": "Failure",
        #             "Data": "User registration failed. Please try again later."
        #         }
        #     }

        # log.info(f"Registration response: {registration_response}")
        full_request = {
            "user_id": user_id,
            "session_id": session_id,
            "client_id": client_id,
            "role": role,
            # "auth_token": auth_token,
            "token":token,
            # "request_type": request_type,
            "interaction": interaction.dict()
        }
        validated_payload = Payload(**full_request)
        result = get_chatbot_response(validated_payload)
        return {"success":False if result.get("error") else True, "data": result} 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))