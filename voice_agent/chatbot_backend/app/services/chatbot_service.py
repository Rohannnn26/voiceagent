"""
Chatbot Service

This module initializes the chatbot engine, session managers, and graph-based flow handlers,
and provides the `get_chatbot_response` function to route user payloads to the appropriate
flow (deterministic or agentic).

Author: Your Name / Team
Date: YYYY-MM-DD
"""

from config.config import JSON_FILE_PATH, REDIS_URL, REDIS_TTL_MINUTES, DB_URI, connection_kwargs
from engine.deterministic_engine import ChatbotEngine
from engine.session_managers.session_store import RedisSessionStore
from engine.session_managers.chatbot_session import ChatbotSessionManager, PayloadSessionManager
from engine.data_loaders.json_loader import load_json
from agentic_flow.main import communicate
from agentic_flow.orchestrator.langgraph_builder import create_langgraph_supervisor
from agentic_flow.utility import classify_id_type

from langgraph.checkpoint.memory import MemorySaver
from monitoring.logger.logger import Logger

from agentic_flow.utility import langfuse

# Initialize logger
log = Logger()
log.info("Chatbot service initialization started.")

# Initialize Redis session store and session managers
store = RedisSessionStore(REDIS_URL, REDIS_TTL_MINUTES)
session_manager = ChatbotSessionManager(store)
payload_session_manager = PayloadSessionManager(store)

# Load flow data and initialize deterministic engine
flow_data = load_json(JSON_FILE_PATH)
engine = ChatbotEngine(flow_data, session_manager, payload_session_manager)

# Initialize LangGraph supervisor and memory-based checkpointing
graph = create_langgraph_supervisor()
checkpointer = MemorySaver()
compiled_graph = graph.compile(checkpointer=checkpointer)

log.info("Chatbot service initialized successfully.")

def get_chatbot_response(payload):
    """
    Entry point to handle chatbot requests.

    Routes the payload to either a deterministic flow engine or an agentic graph
    based on the flow type defined in the payload.

    Args:
        payload (dict or Pydantic object): The input payload containing interaction metadata,
                                           including 'type' and 'input' fields.

    Returns:
        dict or str: Response from the corresponding chatbot processing engine.
    """
    log.info("Received chatbot payload: %s", payload)
    log.info("Starting to classify payload ID type.")        
               
    try:
        # with psycopg.connect(DB_URI, **connection_kwargs) as conn:
        #     checkpointer = PostgresSaver(conn)
        #     checkpointer.setup()

        #     # Compile graph with fresh connection
        graph = create_langgraph_supervisor()
        compiled_graph = graph.compile(checkpointer=checkpointer)
            
        id_response = classify_id_type(payload, compiled_graph)
        log.info("Finished classifying payload ID type.")
        
        if isinstance(id_response, dict):
            log.info(f"Returning options response from classify_id_type.{id_response}")
            return id_response

            
        flow_type = payload.interaction.type

        if not flow_type:
            raise ValueError("Missing or empty 'type' field in payload.")

        # Handle deterministic flow
        if flow_type == "DETERMINISTIC_FLOW":
            input = payload.dict()
            log.info(f"Handling deterministic flow with input: {input.get('interaction', {}).get('input', {}).get('text')}")
            with langfuse.start_as_current_span(name="WMChatBot Deterministic") as span:
                span.update_trace(
                    user_id=payload.user_id,
                    session_id=payload.session_id,
                    input=payload.dict(),
                    tags=[]
                )
            
                log.info(f"button based flow started ..")
                response = engine.handle_input(payload.dict())
                log.info(f"button based flow completed successfully")

                span.update_trace(output={"response": response})

            log.info("Handled via deterministic flow.")
            return response
        
        
        # Handle agentic (LangGraph) flow with scoped Postgres connection
        else:
            # with psycopg.connect(DB_URI, **connection_kwargs) as conn:
            #     checkpointer = PostgresSaver(conn)
            #     checkpointer.setup()

            #     # Compile graph with fresh connection
            #     graph = create_langgraph_supervisor()
            #     compiled_graph = graph.compile(checkpointer=checkpointer)

            #     log.info("PostgreSQL connection established for LangGraph execution.")
                response = communicate(payload, compiled_graph)
                log.info("Handled via agentic (LangGraph) flow.")
                return response

        

    except Exception as e:
        log.exception("Error processing chatbot response: %s", str(e))
        return {
            "status": "Failure",
            "message": "Failed to process chatbot request.",
            "details": str(e),
            "type": "Error",
            "action": "noop"
        }
