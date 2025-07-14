
from langchain_community.agent_toolkits.openapi.toolkit import RequestsToolkit
from langchain_community.utilities.requests import TextRequestsWrapper
from langchain_core.messages import ToolMessage

from app.schemas.request_models import AgentOutput
from monitoring.logger.logger import Logger

import os
import json
from datetime import datetime

log = Logger()

def inject_tool_message(state):
    """
    Appends a ToolMessage to the state based on the latest AIMessage tool call.

    Args:
        state (dict): The current LangGraph state containing 'messages'.
    """
    log.info("Tool message injection Initiated.")
    latest_message = state["messages"][-1]

    if not hasattr(latest_message, "tool_calls") or not latest_message.tool_calls:
        log.info("No tool_calls found in the latest AIMessage. Skipping injection.")
        return

    tool_call = latest_message.tool_calls[0]
    tool_call_id = tool_call["id"]
    assistant_name = tool_call["name"]

    tool_message = ToolMessage(
        content=(
            f"The assistant is now the {assistant_name}. Reflect on the above conversation between the host assistant and the user. "
            f"Remember, you are {assistant_name}, "
            "Do not mention who you are - just act as the proxy for the assistant."
        ),
        tool_call_id=tool_call_id,
    )

    state["messages"].append(tool_message)
    log.info(f"Tool message for {assistant_name} injected successfully")
