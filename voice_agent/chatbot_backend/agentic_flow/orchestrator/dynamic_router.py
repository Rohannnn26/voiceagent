from langgraph.graph import END
from langgraph.prebuilt import tools_condition

from agentic_flow.tools.assistant_tool import agents_tools
from app.schemas.request_models import SupervisorState
from monitoring.logger.logger import Logger

# Initialize logger
log = Logger()

# Router functions for the Agentic Flow Orchestrator
def route_primary_assistant( state: SupervisorState ):
    log.info("Primary Router function Activated.")
    route = tools_condition(state)
    if route == END:
        log.info("Primary Router state has no Tool.")
        return "assistance_final_response_node"
    tool_calls = state["messages"][-1].tool_calls
    if tool_calls:
        if tool_calls[0]["name"] in [tool.__name__ for tool in agents_tools]:
            assistant_name = tool_calls[0]["name"]
            log.info(f"Primary Router state Routed to : {assistant_name}.")
            return assistant_name
        log.info("Primary Router state has no matching Tool on registry.")
        return "supervisor_tools"
    raise ValueError("Invalid route")

# Dynamic Router functions for Report agents
def report_dynamic_router(state):
    log.info("Report Dynamic Router function Activated.")
    # log.info(f"Report Dynamic Router state messages: {state['messages']}")
    # Check if the last message has tool calls
    tool_calls = state["messages"][-1].tool_calls
    if tool_calls:
        # Check tool call name is AgentOutput and status is result, end the conversation.
        if tool_calls[0]["name"] == "AgentOutput" and tool_calls[0]["args"].get("status") == "result":
            return "report_final_response_node"
        # check tool call name is agentoutput and status is out_of_scope, route to leave_node
        if tool_calls[0]["name"] == "AgentOutput" and tool_calls[0]["args"].get("status") == "out_of_scope":
            log.info("Report Dynamic Router state has no Tool.")
            return "leave_node"
        # Check if the tool call is AskBackToUser, route to human_node
        if tool_calls[0]["name"] == "AskBackToUser":
            log.info("Report Dynamic Router state has AskBackToUser Tool.")
            return "report_human_node"
        return "ReportAgent_tools"
    else:
        return "report_final_response_node"

# Dynamic Router functions for Account agents
def account_dynamic_router(state):
    log.info("Account Dynamic Router function Activated.")
    # log.info(f"Account Dynamic Router state messages: {state['messages']}")
    # Check if the last message has tool calls
    tool_calls = state["messages"][-1].tool_calls
    if tool_calls:
        # Check tool call name is AgentOutput and status is result, end the conversation.
        if tool_calls[0]["name"] == "AgentOutput" and tool_calls[0]["args"].get("status") == "result":
            return "account_final_response_node"
        # check tool call name is agentoutput and status is out_of_scope, route to leave_node
        if tool_calls[0]["name"] == "AgentOutput" and tool_calls[0]["args"].get("status") == "out_of_scope":
            log.info("Account Dynamic Router state has no Tool.")
            return "leave_node"
        # Check if the tool call is AskBackToUser, route to human_node
        if tool_calls[0]["name"] == "AskBackToUser":
            log.info("Account Dynamic Router state has AskBackToUser Tool.")
            return "account_human_node"
        return "AccountAgent_tools"
    else:
        return "account_final_response_node"

# Dynamic Router functions for Fund agents
def fund_dynamic_router(state):
    log.info("Fund Dynamic Router function Activated.")
    # log.info(f"Fund Dynamic Router state messages: {state['messages']}")
    # Check if the last message has tool calls
    tool_calls = state["messages"][-1].tool_calls
    if tool_calls:
        # Check tool call name is AgentOutput and status is result, end the conversation.
        if tool_calls[0]["name"] == "AgentOutput" and tool_calls[0]["args"].get("status") == "result":
            return "fund_final_response_node"
        # check tool call name is agentoutput and status is out_of_scope, route to leave_node
        if tool_calls[0]["name"] == "AgentOutput" and tool_calls[0]["args"].get("status") == "out_of_scope":
            log.info("Fund Dynamic Router state has no Tool.")
            return "leave_node"
        # Check if the tool call is AskBackToUser, route to human_node
        if tool_calls[0]["name"] == "AskBackToUser":
            log.info("Fund Dynamic Router state has AskBackToUser Tool.")
            return "fund_human_node"
        return "FundAgent_tools"
    else:
        return "fund_final_response_node"

# Dynamic Router functions for Information centre agents
def information_dynamic_router(state):
    log.info("Information Dynamic Router function Activated.")
    # log.info(f"Information Dynamic Router state messages: {state['messages']}")
    # Check if the last message has tool calls
    tool_calls = state["messages"][-1].tool_calls
    if tool_calls:
        # Check tool call name is AgentOutput and status is result, end the conversation.
        if tool_calls[0]["name"] == "AgentOutput" and tool_calls[0]["args"].get("status") == "result":
            return "information_final_response_node"
        # check tool call name is agentoutput and status is out_of_scope, route to leave_node
        if tool_calls[0]["name"] == "AgentOutput" and tool_calls[0]["args"].get("status") == "out_of_scope":
            log.info("Information Dynamic Router state has no Tool.")
            return "leave_node"
        # Check if the tool call is AskBackToUser, route to human_node
        if tool_calls[0]["name"] == "AskBackToUser":
            log.info("Information Dynamic Router state has AskBackToUser Tool.")
            return "information_human_node"
        return "InformationAgent_tools"
    else:
        return "information_final_response_node"

# Dynamic Router functions for Trading agents
def trading_dynamic_router(state):
    log.info("Trading Dynamic Router function Activated.")
    # log.info(f"Trading Dynamic Router state messages: {state['messages']}")
    # Check if the last message has tool calls
    tool_calls = state["messages"][-1].tool_calls
    if tool_calls:
        # Check tool call name is AgentOutput and status is result, end the conversation.
        if tool_calls[0]["name"] == "AgentOutput" and tool_calls[0]["args"].get("status") == "result":
            return "trading_final_response_node"
        # check tool call name is agentoutput and status is out_of_scope, route to leave_node
        if tool_calls[0]["name"] == "AgentOutput" and tool_calls[0]["args"].get("status") == "out_of_scope":
            log.info("Trading Dynamic Router state has no Tool.")
            return "leave_node"
        # Check if the tool call is AskBackToUser, route to human_node
        if tool_calls[0]["name"] == "AskBackToUser":
            log.info("Trading Dynamic Router state has AskBackToUser Tool.")
            return "trading_human_node"
        return "TradingAgent_tools"
    else:
        return "trading_final_response_node"

# Dynamic Router functions for DP agents
def dp_dynamic_router(state):
    log.info("DP Dynamic Router function Activated.")
    # log.info(f"DP Dynamic Router state messages: {state['messages']}")
    # Check if the last message has tool calls
    tool_calls = state["messages"][-1].tool_calls
    if tool_calls:
        # Check tool call name is AgentOutput and status is result, end the conversation.
        if tool_calls[0]["name"] == "AgentOutput" and tool_calls[0]["args"].get("status") == "result":
            return "dp_final_response_node"
        # check tool call name is agentoutput and status is out_of_scope, route to leave_node
        if tool_calls[0]["name"] == "AgentOutput" and tool_calls[0]["args"].get("status") == "out_of_scope":
            log.info("DP Dynamic Router state has no Tool.")
            return "leave_node"
        # Check if the tool call is AskBackToUser, route to human_node
        if tool_calls[0]["name"] == "AskBackToUser":
            log.info("DP Dynamic Router state has AskBackToUser Tool.")
            return "dp_human_node"
        return "DPAgent_tools"
    else:
        return "dp_final_response_node"