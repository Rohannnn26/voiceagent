from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
from langgraph.types import Command
from langgraph.graph import END

from app.schemas.request_models import Payload, SupervisorState
from agentic_flow.guardrail.faq_grounding import validate_contextual_grounding
from agentic_flow.guardrail.assistance_guard import guard_simple_response 
from agentic_flow.guardrail.api_guard import get_regex_output_guard, get_ban_words_guard, validate_api_response_grounding
from monitoring.logger.logger import Logger

# Initialize logger
log = Logger()


def validate_adjacent_tool_message(messages, id, expected_tool_name):
    """
    Validate if the adjacent message is a ToolMessage with a specific tool name.

    Args:
        messages (list): List of messages.
        id (int): Offset from the end of the list.
        expected_tool_name (str): Tool name to match.

    Returns:
        bool: True if the adjacent message matches the expected ToolMessage.
    """
    adjacent_id = id + 1  # Adjust to get the message before the last one

    if not isinstance(messages, list) or len(messages) < adjacent_id:
        log.info("Messages list is too short or not a list. Skipping validation.")
        return False

    adjacent_msg = messages[-adjacent_id]

    if not isinstance(adjacent_msg, ToolMessage):
        log.info("Adjacent message is not a ToolMessage.")
        return False

    return adjacent_msg.name == expected_tool_name

def extract_message_content(messages, id):
    """
    Extracts content from a message at a given offset from the end of the list.

    Args:
        messages (list): List of message objects.
        id (int): Index offset from the end.

    Returns:
        str: Extracted message content, or None if invalid.
    """
    adjacent_id = id + 1
    if not isinstance(messages, list) or len(messages) < adjacent_id:
        log.warning(f"Message list too short or invalid. Cannot extract message at offset {adjacent_id}.")
        return None

    content = messages[-adjacent_id].content
    log.info(f"Extracted message content at position -{adjacent_id}")
    return content

def grounding_pass_signal(tool_response: dict) -> bool:
    """
    Evaluates if the grounding validator passed based on defined strict criteria.

    Args:
        tool_response (dict): Output from GroundingValidatorTool.

    Returns:
        bool: True if grounding passes, False otherwise.
    """
    query_relevance = tool_response.get("query_response_relevance", "")
    chunk_alignment = tool_response.get("response_chunk_alignment", "")
    dialogue_cont = tool_response.get("dialogue_continuity", "")
    
    log.info(f"Grounding validation criteria: Query relevance: {query_relevance}, "
             f"Chunk alignment: {chunk_alignment}, Dialogue continuity: {dialogue_cont}")
    
    result = (
        query_relevance == "High"
        and chunk_alignment == "Aligned"
        and dialogue_cont == "Coherent"
    )
    
    log.info(f"Grounding validation result: {'Pass' if result else 'Fail'}")
    return result

def api_pass_signal(tool_response: dict) -> bool:
    """
    Evaluates if the API response passes based on defined criteria.

    Args:
        tool_response (dict): Output from GroundingValidatorTool.

    Returns:
        bool: True if API response passes, False otherwise.
    """
    query_relevance = tool_response.get("query_response_relevance", "")
    chunk_alignment = tool_response.get("response_chunk_alignment", "")
    
    log.info(f"API response validation criteria: Query relevance: {query_relevance}, "
             f"Chunk alignment: {chunk_alignment}")
    
    result = (
        query_relevance == "High"
        and chunk_alignment == "Aligned"
    )
    
    log.info(f"API response validation result: {'Pass' if result else 'Fail'}")
    return result

def assisatnce_pass_signal(tool_response: dict) -> bool:
    """
    Evaluates if the assistance guard passed based on defined criteria.

    Args:
        tool_response (dict): Output from AssistanceGuardTool.

    Returns:
        bool: True if assistance passes, False otherwise.
    """
    intent_type = tool_response.get("intent_type", "")
    reason = tool_response.get("reason", "")
    
    # Define criteria for passing the assistance guard
    # result = intent_type != "Other"
    result = intent_type not in ["Other", "Apology"]
    if not result:
        log.info(f"Assistance guard failed due to intent type being 'Other' or empty. with reason: {reason}")
    
    log.info(f"Assistance guard result: {'Pass' if result else 'Fail'}")
    return result


def assistance_final_response_node(state: SupervisorState):
    """
    Process messages for assistance check.
    """
    log.info("Starting assistance check messages extraction...")
    
    query = state.get("payload", Payload).interaction.input.text
    messages = state.get("messages", [])
    
    # Get the last message
    id = 1
    last_message = messages[-id]
    
    if isinstance(last_message, AIMessage) and (not hasattr(last_message, "tool_calls") or not last_message.tool_calls):
        log.info("Found AIMessage without tool calls - proceeding with assistance guard check")
        
        result = guard_simple_response(last_message.content)
        log.info(f"Assistance guard check result: {result.tool_calls[0]['args']}")
        flag = assisatnce_pass_signal(result.tool_calls[0]['args'])
        log.info(f"Assistance guard check result: {flag}")
        regex_flag = get_regex_output_guard(last_message.content)
        log.info(f"Regex guard check result: {regex_flag}")
        ban_flag = get_ban_words_guard(last_message.content)
        log.info(f"Ban words guard check result: {ban_flag}")
        if flag and regex_flag is True and ban_flag is True:
            log.info("Assistance guard check passed successfully.")
            return Command(
                # End flow
                goto=END
            )
        else:
            content = ("I sincerely apologize for not able to fulfill your request.")
            log.info(f"Assistance guard check failed with reason: {content}")
            messages.append(AIMessage(content=content))
            log.info("Appending failure message to messages history.")
            response = {
                "message": content,
                "status": "result",
            }
            return Command(
                # update the message history
                update={"messages": messages,
                        "response": response},
                # control flow
                goto=END
            )

def process_final_response(state: SupervisorState, goto_target: str) -> Command:
    """
    Validate the last tool call message and update the message history.
    
    If validations (regex and ban words) fail, return a Command directing flow to the specified goto_target.
    Otherwise, append a completion message and return a Command to end the flow.
    
    Args:
        state (SupervisorState): The current state containing messages and payload.
        goto_target (str): The agent name to route to if validations fail.
        
    Returns:
        Command: A command object with updated messages and the appropriate control flow directive.
    """
    messages = state.get("messages", [])
    
    if not messages:
        log.info("No messages found in state.")
        return Command(update={"messages": messages}, goto=END)
    
    last_message = messages[-1]
    
    # Verify the last message came from a tool call
    if isinstance(last_message, AIMessage) and hasattr(last_message, "tool_calls") and last_message.tool_calls:
        tool_call = last_message.tool_calls[0]
        if tool_call.get("name") == "AgentOutput" and tool_call["args"].get("status") == "result":
            tool_call_id = tool_call["id"]
            message_text = tool_call["args"].get("message", "")
            
            # Regex check
            regex_flag = get_regex_output_guard(message_text)
            if regex_flag is not True:
                log.info(f"Regex validation failed: {regex_flag}")
                messages.append(ToolMessage(content=str(regex_flag), tool_call_id=tool_call_id))
                return Command(update={"messages": messages}, goto=goto_target)
            
            # Ban word check
            ban_flag = get_ban_words_guard(message_text)
            if ban_flag is not True:
                log.info(f"Banned words validation failed: {ban_flag}")
                messages.append(ToolMessage(content=str(ban_flag), tool_call_id=tool_call_id))
                return Command(update={"messages": messages}, goto=goto_target)
            log.info("Regex and ban words validation passed successfully")
        id = 1
        # Proceed with API grounding validation if the tool call is from API
        if validate_adjacent_tool_message(messages, id, "request_post"):
            log.info("API tool call message found - proceeding with API grounding validation")
            message_text = tool_call["args"].get("message", "")
            api_tool_call_data = extract_message_content(messages, 1)
            result = validate_api_response_grounding(
                response=message_text,
                chunk=api_tool_call_data
            )
            log.info(f"API tool call grounding validation result: {result.tool_calls[0]['args']}")
            api_flag = api_pass_signal(result.tool_calls[0]['args'])
                
            if api_flag is not True:
                # If API grounding validation fails, append issues to messages
                content = (result.tool_calls[0]['args'].get("issues", ""))
                log.info(f"API tool call grounding validation failed ..")
                messages.append(ToolMessage(content=content, tool_call_id=tool_call_id))
                return Command(update={"messages": messages}, goto=goto_target)

            # If API grounding validation passes, append a completion message
            log.info("API grounding validation passed successfully")

        # for FAQ grounding if RAG data retrive and context summury happend then only we can validate the grounding
        if validate_adjacent_tool_message(messages, id, "faq_knowledge_base"):
            log.info("FAQ adjacent message is from the FAQ knowledge base.")
            query = state.get("payload", Payload).interaction.input.text
            message_text = tool_call["args"].get("message", "")
            rag_data = extract_message_content(messages, id)
            tool_call = state["messages"][-1].tool_calls[0]
            log.info("Proceeding with contextual grounding validation")
            
            result = validate_contextual_grounding(
                query=query,
                response=message_text,
                # Use the extracted RAG data for grounding validation
                chunk=rag_data,
                dialogue_history=""
            )
            log.info(f"Grounding validation result: {result.tool_calls[0]['args']}")
            flag = grounding_pass_signal(result.tool_calls[0]['args'])
            if flag is not True:
                content = (result.tool_calls[0]['args'].get("issues", ""))
                log.info(f"Grounding validation failed with issues: {content}")
                messages.append(ToolMessage(content=content, tool_call_id=tool_call["id"]))
                return Command(
                        # update the message history
                        update={"messages": messages},
                        # control flow
                        goto=goto_target
                    )
            log.info("Grounding validation passed successfully")

        # Append a completion message to the messages
        content = ("This query response has been completed.")
        log.info("Final response processing completed successfully")
        messages.append(ToolMessage(content=content, tool_call_id=tool_call_id))
        return Command(update={"messages": messages}, goto=END)
    
    # Fallback if message structure is not as expected
    log.info("No valid tool call found in the last message.")
    response = {
        "message": "I apologize, This query appears to be outside of my scope.",
        "status": "result"
    }
    return Command(update={"response" : response}, goto=END)


def report_final_response_node(state: SupervisorState) -> Command:
    """
    Process final response for Report flow.
    """
    log.info("Starting report response check...")
    return process_final_response(state, goto_target="ReportAgent")


def dp_final_response_node(state: SupervisorState) -> Command:
    """
    Process final response for Database flow.
    """
    log.info("Starting database response check...")
    return process_final_response(state, goto_target="DPAgent")


def account_final_response_node(state: SupervisorState) -> Command:
    """
    Process final response for Account flow.
    """
    log.info("Starting account response check...")
    return process_final_response(state, goto_target="AccountAgent")


def trading_final_response_node(state: SupervisorState) -> Command:
    """
    Process final response for Trading flow.
    """
    log.info("Starting trading response check...")
    return process_final_response(state, goto_target="TradingAgent")

    
def fund_final_response_node(state: SupervisorState) -> Command:
    """
    Process final response for Fund flow.
    """
    log.info("Starting fund response check...")
    return process_final_response(state, goto_target="FundAgent")

def information_final_response_node(state: SupervisorState):
    """ Process final response for Information Centre flow.
    """
    log.info("Starting FAQ grounding messages extraction...")
    return process_final_response(state, goto_target="InformationCentreAgent")