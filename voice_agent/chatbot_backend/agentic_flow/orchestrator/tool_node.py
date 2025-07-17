from langchain_core.messages import ToolMessage, AIMessage
from langchain_core.runnables import RunnableLambda
from langgraph.prebuilt import ToolNode
from agentic_flow.tools.assistant_tool import agents_tools
from agentic_flow.tools.react_tool import react_tools, information_centre_tools
from app.schemas.request_models import SupervisorState
from agentic_flow.utility import get_tool_name
from monitoring.logger.logger import Logger

# Initialize logger
log = Logger()

# Falback node
def handle_tool_error(state: SupervisorState) -> dict:
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\n please fix your mistakes.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }

# ToolNode class to handle tool execution with fallbacks
def create_tool_node_with_fallback(tools: list) -> dict:
    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )

def fake_tool_node(state: SupervisorState):
    """A fake tool node that simulates a tool call and returns a message."""
    log.info("Executing fake_tool_node function - simulating tool call")
    
    messages = state.get("messages", [])
    
    last_message = messages[-1]
    if isinstance(last_message, AIMessage) and hasattr(last_message, "tool_calls") and last_message.tool_calls:
        tool_call = state["messages"][-1].tool_calls[0]
        tool_call_id = tool_call["id"]
        log.info(f"Found fake tool call with id: {tool_call_id}")
        tools_list = ', '.join([tool.__name__ for tool in agents_tools])
        content = f"You have access to following tools only: {tools_list}."
        messages.append(
            ToolMessage(
                content=content,
                tool_call_id=tool_call_id,
            )
        )
        
        log.info("Fake tool node executed, returning simulated messages")
        
        return {
            "messages": messages
        }

def report_fake_tool_node(state: SupervisorState):
    """A fake tool node for the Report Agent that simulates a tool call and returns a message."""
    log.info("Executing report_fake_tool_node function - simulating tool call")
    
    messages = state.get("messages", [])
    
    last_message = messages[-1]
    if isinstance(last_message, AIMessage) and hasattr(last_message, "tool_calls") and last_message.tool_calls:
        tool_call = state["messages"][-1].tool_calls[0]
        tool_call_id = tool_call["id"]
        log.info(f"Found fake tool call with id: {tool_call_id}")
    
        content = (
            "You only have access to following tools only:"
            + ', '.join([get_tool_name(tool) for tool in react_tools])
        )
        
        messages.append(
            ToolMessage(
                content=content,
                tool_call_id=tool_call_id,
            )
        )
        
        log.info("Report fake tool node executed, returning simulated messages")
        
        return {
            "messages": messages
        }

def account_fake_tool_node(state: SupervisorState):
    """A fake tool node for the Account Agent that simulates a tool call and returns a message."""
    log.info("Executing account_fake_tool_node function - simulating tool call")
    
    messages = state.get("messages", [])
    
    last_message = messages[-1]
    if isinstance(last_message, AIMessage) and hasattr(last_message, "tool_calls") and last_message.tool_calls:
        tool_call = state["messages"][-1].tool_calls[0]
        tool_call_id = tool_call["id"]
        log.info(f"Found fake tool call with id: {tool_call_id}")
    
        content = (
            "You only have access to following tools only: "
            + ', '.join([get_tool_name(tool) for tool in react_tools])
        )
        
        messages.append(
            ToolMessage(
                content=content,
                tool_call_id=tool_call_id,
            )
        )
        
        log.info("Account fake tool node executed, returning simulated messages")
        
        return {
            "messages": messages
        }

def fund_fake_tool_node(state: SupervisorState):
    """A fake tool node for the Fund Agent that simulates a tool call and returns a message."""
    log.info("Executing fund_fake_tool_node function - simulating tool call")
    
    messages = state.get("messages", [])
    
    last_message = messages[-1]
    if isinstance(last_message, AIMessage) and hasattr(last_message, "tool_calls") and last_message.tool_calls:
        tool_call = state["messages"][-1].tool_calls[0]
        tool_call_id = tool_call["id"]
        log.info(f"Found fake tool call with id: {tool_call_id}")
    
        content = (
            "You only have access to following tools only: "
            + ', '.join([get_tool_name(tool) for tool in react_tools])
        )
        
        messages.append(
            ToolMessage(
                content=content,
                tool_call_id=tool_call_id,
            )
        )
        
        log.info("Fund fake tool node executed, returning simulated messages")
        
        return {
            "messages": messages
        }

def information_fake_tool_node(state: SupervisorState):
    """A tool node that provides information about available tools."""
    log.info("Executing information_tool_node function - providing tool information")
    
    messages = state.get("messages", [])
    last_message = messages[-1]
    if isinstance(last_message, AIMessage) and hasattr(last_message, "tool_calls") and last_message.tool_calls:
        tool_call = state["messages"][-1].tool_calls[0]
        tool_call_id = tool_call["id"]
        log.info(f"Found fake tool call with id: {tool_call_id}")
    
        content = (
            "You only have access to following tools only: "
            + ', '.join([get_tool_name(tool) for tool in information_centre_tools])
        )
        
        messages.append(
            ToolMessage(
                content=content,
                tool_call_id="informational_tool_node"
            )
        )
        
        log.info("Informational tool node executed, returning messages with tool information")
        
        return {
            "messages": messages
        }

def trading_fake_tool_node(state: SupervisorState):
    """A fake tool node for the Trading Agent that simulates a tool call and returns a message."""
    log.info("Executing trading_fake_tool_node function - simulating tool call")
    
    messages = state.get("messages", [])
    
    last_message = messages[-1]
    if isinstance(last_message, AIMessage) and hasattr(last_message, "tool_calls") and last_message.tool_calls:
        tool_call = state["messages"][-1].tool_calls[0]
        tool_call_id = tool_call["id"]
        log.info(f"Found fake tool call with id: {tool_call_id}")
    
        content = (
            "You only have access to following tools only: "
            + ', '.join([get_tool_name(tool) for tool in react_tools])
        )
        
        messages.append(
            ToolMessage(
                content=content,
                tool_call_id=tool_call_id,
            )
        )
        
        log.info("Trading fake tool node executed, returning simulated messages")
        
        return {
            "messages": messages
        }

def dp_fake_tool_node(state: SupervisorState):
    """A fake tool node for the DP Agent that simulates a tool call and returns a message."""
    log.info("Executing dp_fake_tool_node function - simulating tool call")
    
    messages = state.get("messages", [])
    
    last_message = messages[-1]
    if isinstance(last_message, AIMessage) and hasattr(last_message, "tool_calls") and last_message.tool_calls:
        tool_call = state["messages"][-1].tool_calls[0]
        tool_call_id = tool_call["id"]
        log.info(f"Found fake tool call with id: {tool_call_id}")
    
        content = (
            "You only have access to following tools only:"
            + ', '.join([get_tool_name(tool) for tool in react_tools])
        )
        
        messages.append(
            ToolMessage(
                content=content,
                tool_call_id=tool_call_id,
            )
        )
        
        log.info("DP fake tool node executed, returning simulated messages")
        
        return {
            "messages": messages
        }
