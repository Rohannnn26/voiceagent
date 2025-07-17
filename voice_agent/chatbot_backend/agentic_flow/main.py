"""
Main entry point for the application module handling user interaction via a SupervisorAgent graph.
"""

import json

from monitoring.logger.event_logging import _print_event
from monitoring.logger.logger import Logger
from langgraph.types import Command
from agentic_flow.utility import generate_request_id, langfuse
import traceback
from langfuse.langchain import CallbackHandler
from agentic_flow.utility.state_utils import generate_remove_messages
# Initialize the logger
log = Logger()


def communicate(payload, graph):
    """
    Processes user input through the provided graph object (e.g., SupervisorAgent)
    and returns a structured response.

    Args:
        payload (dict): Dictionary containing interaction metadata including user input.
        graph: Graph interface instance with `.stream()` and `.get_state()` methods.

    Returns:
        str: A JSON-formatted string with the result from the SupervisorAgent graph.
    """
    try:
        # Extract user query from payload
        query = payload.interaction.input.text
        request_id = payload.interaction.request_id
        log.info(f"Payload request id is : {request_id}")
        if not query:
            log.warning("Received empty query in payload.")
            return {
                "status": "Failure",
                "message": "Empty query provided.",
                "action": "result"
            }

        # Extract session ID for tracking conversation thread
        session_id = payload.session_id

        # intialize Langfuse callback handler for tracing
        langfuse_handler = CallbackHandler()

        # Configuration object for graph interaction
        config = {
            "configurable": {
                "thread_id": session_id
            },
            "callbacks": [langfuse_handler],
        }

        # config = {
        #     "configurable": {
        #         "thread_id": request_id
        #     },
        #     "callbacks": [langfuse_handler],  # Add Langfuse callback handler for tracing
        # }

        _printed = set()  # Track printed events to avoid duplication
        snapshot_state = graph.get_state(config)
        # if snapshot_state.values.get("inrpt"):
        if len(snapshot_state.tasks)>0 and len(snapshot_state.tasks[0].interrupts)>0:
            log.info(f"Interupt Resume: >>")
            # add the ask back user reponse to command
            command = Command(resume=query)
            # Resume the graph execution
            # for event in graph.stream(command, config, stream_mode="values"):
            #     _print_event(event, _printed)
            # Set trace attributes dynamically via enclosing span
            with langfuse.start_as_current_span(name="WMChatBot Langgraph") as span:
                log.info(f"Starting interrupt resume with request_id: {request_id}")
                span.update_trace(
                    user_id=payload.user_id,
                    session_id=session_id,
                    input=command,
                    tags=[request_id]
                )
            
                log.info(f"Invoking graph with interrupt resume command")
                result = graph.invoke(command, config, stream_mode="values")
                log.info(f"Interrupt resume completed successfully")
            
                span.update_trace(output={"response": result})
            
        else:
            # New Request id generated
            new_request_id = generate_request_id()
            # Create a new InteractionV2 object with updated request_id
            updated_interaction = payload.interaction.copy(update={"request_id": new_request_id})
            # Create a new Payload object with updated interaction
            updated_payload = payload.copy(update={"interaction": updated_interaction})
            log.info(f"new request id: {new_request_id}")
            # Initialize Langfuse callback handler for tracing
            langfuse_handler = CallbackHandler()
            # config = {
            #     "configurable": {
            #         "thread_id": new_request_id
            #     },
            #     "callbacks": [langfuse_handler],  # Add Langfuse callback handler for tracing
            # }

            # Stream events through the graph based on input
            # for event in graph.stream({"messages": ("user", query), "payload": updated_payload}, config, stream_mode="values"):
            #     _print_event(event, _printed)
            log.info(f"Starting new graph invocation with request_id: {new_request_id}")
            with langfuse.start_as_current_span(name="WMChatBot Langgraph") as span:
                span.update_trace(
                    user_id=payload.user_id,
                    session_id=session_id,
                    input={"messages": ("user", query), "payload": updated_payload},
                    tags=[new_request_id]
                )
                
                log.info(f"Invoking graph with user query: '{query}'")
                result = graph.invoke({"messages": ("user", query), "payload": updated_payload}, config, stream_mode="values")
                log.info(f"Graph invocation completed successfully")
            
                span.update_trace(output={"response": result})
            

        # Retrieve latest state of the conversation
        snapshot_state = graph.get_state(config)
        # log.info(f"Snapshot Data: {snapshot_state}")

        if len(snapshot_state.tasks)>0 and len(snapshot_state.tasks[0].interrupts)>0:
            message = snapshot_state.tasks[0].interrupts[0].value
            log.info(f"Intrupted Messages goes to User.")
        else:
            log.info(f"Normal Messages goes to User.")
            message = snapshot_state.values.get("response", {}).get("message")

        new_request_id = snapshot_state.values.get("payload", {}).interaction.request_id
        log.info(f"Request id is : {new_request_id}")

        # Construct final response
        response = {
            "status": "Success",
            "message": message,
            "action": "result",
            "request_id" : new_request_id
        }

        log.info("Response generated successfully for session_id: %s", session_id)
        return response

    except Exception as e:
        # Log the exception details and return a failure response
        snapshot_state = graph.get_state(config)
        log.info(f"Snapshot Data in except part : {len(snapshot_state.values.get('messages', {}))}")
        last_message_first_exp = snapshot_state.values.get("messages", {})[-1]
        log.info(f"Last message in except state: {last_message_first_exp}, type: {type(last_message_first_exp)}")

        payload_json = snapshot_state.values.get("payload", {})
        new_request_id=""
        if 'interaction' in payload_json:
            new_request_id = payload_json.request_id
        
        tool_message_text =  "This query response has been completed."
        msg = snapshot_state.values.get("messages")
        remove_instructions = generate_remove_messages(msg, tool_message_text)
        log.info(f"Messages to remove: {len(remove_instructions)}")

        # Apply the RemoveMessage instructions
        graph.update_state(config, values={"messages": remove_instructions})
        
        recover_snapshot_state = graph.get_state(config)
        log.info(f"Snapshot Data in recover part : {len(recover_snapshot_state.values.get('messages', {}))}")
        last_message_recover = recover_snapshot_state.values.get("messages", {})[-1]
        log.info(f"Last message in recover state: {last_message_recover}, type: {type(last_message_recover)}")
        return {
            "status": "Failure",
            "message": f"I sincerely apologize for not able to fulfill your request.",
            "action": "result",
            "request_id" : new_request_id
        }
