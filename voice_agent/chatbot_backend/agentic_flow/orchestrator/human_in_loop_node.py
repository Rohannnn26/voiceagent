from langgraph.types import interrupt
from langchain_core.messages import ToolMessage

from app.schemas.request_models import SupervisorState
from agentic_flow.guardrail.ask_back_guard import ask_back_final_check
from monitoring.logger.logger import Logger

# Initialize logger
log = Logger()


# Human-in-the-loop nodes for various agent dialog flows
def report_human_node(state: SupervisorState):
    """Handles human input for the Report Agent dialog flow."""
    log.info("Report Human Node Activated.")
    # log.info(f"Report Human Node state messages: {state['messages']}")
    
    last_message = state["messages"][-1]
    tool_call_id = last_message.tool_calls[0]["id"]
    ask_back_message = last_message.tool_calls[0]["args"].get("interrupt_message", "")
    
    log.info(f"Ask back content: {last_message.tool_calls[0]}")
    cmd = ask_back_final_check(ask_back_message, "ReportAgent", tool_call_id, state["messages"])
    if cmd is not None:
        return cmd
    user_response = interrupt(ask_back_message)
    log.info(f"User input received: {user_response}")
    
    updated_messages = state["messages"] + [
        ToolMessage(content=user_response, tool_call_id=tool_call_id)
    ]
    
    return {"messages": updated_messages}

def account_human_node(state: SupervisorState):
    """Handles human input for the Account Agent dialog flow."""
    log.info("Account Human Node Activated.")
    # log.info(f"Account Human Node state messages: {state['messages']}")
    
    last_message = state["messages"][-1]
    tool_call_id = last_message.tool_calls[0]["id"]
    ask_back_message = last_message.tool_calls[0]["args"].get("interrupt_message", "")
    
    log.info(f"Ask back content: {last_message.tool_calls[0]}")
    cmd = ask_back_final_check(ask_back_message, "AccountAgent", tool_call_id, state["messages"])
    if cmd is not None:
        return cmd
    user_response = interrupt(ask_back_message)
    log.info(f"User input received: {user_response}")
    
    updated_messages = state["messages"] + [
        ToolMessage(content=user_response, tool_call_id=tool_call_id)
    ]
    
    return {"messages": updated_messages}

def fund_human_node(state: SupervisorState):
    """Handles human input for the Fund Agent dialog flow."""
    log.info("Fund Human Node Activated.")
    # log.info(f"Fund Human Node state messages: {state['messages']}")
    
    last_message = state["messages"][-1]
    tool_call_id = last_message.tool_calls[0]["id"]
    ask_back_message = last_message.tool_calls[0]["args"].get("interrupt_message", "")
    
    log.info(f"Ask back content: {last_message.tool_calls[0]}")
    cmd = ask_back_final_check(ask_back_message, "FundAgent", tool_call_id, state["messages"])
    if cmd is not None:
        return cmd
    user_response = interrupt(ask_back_message)
    log.info(f"User input received: {user_response}")
    
    updated_messages = state["messages"] + [
        ToolMessage(content=user_response, tool_call_id=tool_call_id)
    ]
    
    return {"messages": updated_messages}

def trading_human_node(state: SupervisorState):
    """Handles human input for the Trading Agent dialog flow."""
    log.info("Trading Human Node Activated.")
    # log.info(f"Trading Human Node state messages: {state['messages']}")
    
    last_message = state["messages"][-1]
    tool_call_id = last_message.tool_calls[0]["id"]
    ask_back_message = last_message.tool_calls[0]["args"].get("interrupt_message", "")
    
    log.info(f"Ask back content: {last_message.tool_calls[0]}")
    cmd = ask_back_final_check(ask_back_message, "TradingAgent", tool_call_id, state["messages"])
    if cmd is not None:
        return cmd
    user_response = interrupt(ask_back_message)
    log.info(f"User input received: {user_response}")
    
    updated_messages = state["messages"] + [
        ToolMessage(content=user_response, tool_call_id=tool_call_id)
    ]
    
    return {"messages": updated_messages}

def information_human_node(state: SupervisorState):
    """Handles human input for the Information Agent dialog flow."""
    log.info("Information Human Node Activated.")
    # log.info(f"Information Human Node state messages: {state['messages']}")
    
    last_message = state["messages"][-1]
    tool_call_id = last_message.tool_calls[0]["id"]
    ask_back_message = last_message.tool_calls[0]["args"].get("interrupt_message", "")
    
    log.info(f"Ask back content: {last_message.tool_calls[0]}")
    cmd = ask_back_final_check(ask_back_message, "InformationCentreAgent", tool_call_id, state["messages"])
    if cmd is not None:
        return cmd
    user_response = interrupt(ask_back_message)
    log.info(f"User input received: {user_response}")
    
    updated_messages = state["messages"] + [
        ToolMessage(content=user_response, tool_call_id=tool_call_id)
    ]
    
    return {"messages": updated_messages}

def dp_human_node(state: SupervisorState):
    """Handles human input for the DP Agent dialog flow."""
    log.info("DP Human Node Activated.")
    # log.info(f"DP Human Node state messages: {state['messages']}")
    
    last_message = state["messages"][-1]
    tool_call_id = last_message.tool_calls[0]["id"]
    ask_back_message = last_message.tool_calls[0]["args"].get("interrupt_message", "")
    
    log.info(f"Ask back content: {last_message.tool_calls[0]}")
    cmd = ask_back_final_check(ask_back_message, "DPAgent", tool_call_id, state["messages"])
    if cmd is not None:
        return cmd
    user_response = interrupt(ask_back_message)
    log.info(f"User input received: {user_response}")
    
    updated_messages = state["messages"] + [
        ToolMessage(content=user_response, tool_call_id=tool_call_id)
    ]
    
    return {"messages": updated_messages}