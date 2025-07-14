from langchain_core.messages import ToolMessage

from app.schemas.request_models import SupervisorState
from monitoring.logger.logger import Logger

# Initialize logger
log = Logger()


# leave node function to pop the dialog stack and return to the main assistant
def leave_node(state: SupervisorState):
    """Pop the dialog stack and return to the main assistant.
    This lets the full graph explicitly track the dialog flow and delegate control
    to specific sub-graphs.
    """
    log.info("Executing leave_node function - popping dialog stack")
    messages = []
    if state["messages"][-1].tool_calls:
        # Note: Doesn't currently handle the edge case where the llm performs parallel tool calls
        tool_call = state["messages"][-1].tool_calls[0]
        log.info(f"Found tool call with id: {tool_call['id']}")
        # Extract the content from the tool message which contains the user's new question
        # This is a human-in-the-loop scenario where the original flow was interrupted
        content = (
            "Resuming dialog with the host assistant. Please reflect on the past conversation and assist the user as needed."
            "I've received this query which was outside my initial processing scope. "
            "Please address their new request, captured during the recent AskBackToUser step and originating from the tool message."
        )
        
        messages.append(
            ToolMessage(
            content=content,
            tool_call_id=tool_call["id"],
            )
        )
        log.info("Created tool message response for resuming dialog")
    else:
        log.info("No tool calls found in the last message")
    
    log.info("Leaving node and returning to main assistant")
    return {
        "messages": messages
    }