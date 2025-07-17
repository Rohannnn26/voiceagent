
from langchain_community.agent_toolkits.openapi.toolkit import RequestsToolkit
from langchain_community.utilities.requests import TextRequestsWrapper
from langchain_core.messages import ToolMessage
from langchain_core.tools import Tool
from langgraph.types import interrupt

from monitoring.logger.logger import Logger
from app.schemas.request_models import AgentOutput
from typing import Dict, Any, Optional

log = Logger()

def build_requests_toolkit(sessionid: str, token: str) -> RequestsToolkit:
    """
    Builds a RequestsToolkit with the necessary authentication headers.

    Args:
        sessionid (str): The session ID to authenticate the request.
        token (str): The token to authenticate the request.

    Returns:
        RequestsToolkit: A configured requests toolkit.
    """
    headers = {
        "sessionid": sessionid,
        "token": token,
        "User-Agent": "Mozilla/5.0",
    }
    return RequestsToolkit(
        requests_wrapper=TextRequestsWrapper(headers=headers),
        allow_dangerous_requests=True,
    )

def get_post_tools(sessionid: str, token: str):
    """
    Retrieves only the POST request tool from a custom RequestsToolkit.

    Args:
        sessionid (str): Session ID for authentication.
        token (str): Auth token for the toolkit.

    Returns:
        list: List of tools that match the POST request handler.
    """
    log.info("Tool building started.")

    toolkit = build_requests_toolkit(sessionid, token)
    tools = [tool for tool in toolkit.get_tools() if tool.name == "requests_post"]

    log.info("Tool building completed.")
    log.info(f"Available tools for Agent: {[tool.name for tool in tools]}")
    return tools

def create_user_interrupt_tool():
    """
    Creates a tool that handles user interruptions in a LangGraph flow.
    
    This tool allows the agent to request input from the user during execution
    and process the response before continuing.
    
    Returns:
        Tool: A tool for handling user interruptions
    """
    def user_interrupt(query: str) -> str:
        """
        Requests input from the user and returns their response.
        
        Args:
            query (str): The message to show to the user when requesting input or confirmation.
            
        Returns:
            str: The user's response
        """
        log.info(f"Agent requesting user input: {query}")
        try:
            intrupt_reponse = interrupt(query)
            log.info(f"Received user response: {intrupt_reponse}")
            return intrupt_reponse
        except Exception as e:
            log.error(f"Error handling user interrupt: {str(e)}")
            return "Failed to get user response due to an error."
    
    return Tool(
        name="ask_back",
        description="Use this tool when you need to ask the user a question or request additional information",
        func=user_interrupt,
    )

def create_output_formatter_tool():
    """
    Returns a LangChain tool that formats output using the AgentOutput schema.
    
    Returns:
        Tool: A tool that validates and formats agent output according to AgentOutput schema
    """

    def format_output(input_str: str) -> str:
        """
        Parses a JSON string into AgentOutput format.
        
        Args:
            input_str (str): JSON string containing at least 'message' and 'status' fields
            
        Returns:
            str: JSON string of the validated AgentOutput object
        """
        import json

        try:
            # Parse input string to dict
            output_data = json.loads(input_str)
            # Validate and create AgentOutput
            formatted_output = AgentOutput(**output_data)
            log.info(f"Agent output formatted with status: {formatted_output.status}")
            return formatted_output.json()
        except json.JSONDecodeError as e:
            log.error(f"Invalid JSON in agent output: {str(e)}")
            return f"Failed to format output: Invalid JSON - {str(e)}"
        except Exception as e:
            log.error(f"Error formatting agent output: {str(e)}")
            return f"Failed to format output: {str(e)}"

    return Tool(
        name="format_output",
        description=(
            "Use this tool to format your final response according to the required schema. "
            "Input must be a JSON string with `message` and `status`."
        ),
        func=format_output,
    )

def get_tool_name(tool_obj):
    if hasattr(tool_obj, 'name'):
        return tool_obj.name  # for LangChain tools
    elif hasattr(tool_obj, '__name__'):
        return tool_obj.__name__  # for normal functions
    elif hasattr(tool_obj, '__class__'):
        return tool_obj.__class__.__name__  # for Pydantic classes
    return str(tool_obj)  # fallback