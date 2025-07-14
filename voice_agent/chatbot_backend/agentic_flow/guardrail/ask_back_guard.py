from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
from langgraph.types import Command
from langgraph.graph import END

from agentic_flow.guardrail.api_guard import get_regex_output_guard, get_ban_words_guard, validate_api_response_grounding
from monitoring.logger.logger import Logger

# Initialize logger
log = Logger()


def ask_back_final_check(ask_back_message, goto_target, tool_call_id, messages):
    """
    Final check for Ask Back messages to ensure they are valid before proceeding.
    This function validates the ask-back message against regex and banned words.
    """
    log.info("Starting Ask Back final check...")

    # Validate the ask-back message
    # Regex check
    regex_flag = get_regex_output_guard(ask_back_message)
    if regex_flag is not True:
        log.info(f"Regex validation failed: {regex_flag}")
        messages.append(ToolMessage(content=str(regex_flag), tool_call_id=tool_call_id))
        return Command(update={"messages": messages}, goto=goto_target)
    
    # Ban word check
    ban_flag = get_ban_words_guard(ask_back_message)
    if ban_flag is not True:
        log.info(f"Banned words validation failed: {ban_flag}")
        messages.append(ToolMessage(content=str(ban_flag), tool_call_id=tool_call_id))
        return Command(update={"messages": messages}, goto=goto_target)
    log.info("Regex and ban words validation passed successfully")

    log.info("Ask Back final check completed - valid response received")