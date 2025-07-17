from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal, List
from langchain_core.prompts import ChatPromptTemplate
from agentic_flow.utility import get_llm_model  # Your existing utility
from monitoring.logger.logger import Logger
from config.config import JSON_FILE_PATH
from langfuse.langchain import CallbackHandler
import json

# Initialize logger
log = Logger()


def extract_id_types_from_json(role):
    """
    Reads the JSON file and extracts id and text of buttons from initial_client.available_choices.

    Returns:
        list: A list of dictionaries with 'id' and 'text'.
    """
    log.info("Reading JSON file to extract id_types.")
    try:
        with open(JSON_FILE_PATH, 'r') as file:
            data = json.load(file)
            log.info("Loaded JSON content.")

        id_types = []
        choices = data.get("initial_client" if role.lower() == 'client' else "initial_partner", {}).get("available_choices", [])
        for button in choices:
            btn_id = button.get("id")
            btn_text = button.get("text")
            if btn_id and btn_text:
                id_types.append({"id": btn_id, "text": btn_text})

            if not any(item["id"] == "home" for item in id_types):
                id_types.append({"id": "home", "text": "home"})
                log.info("Added default 'home' button to id_types.")

        log.info("Extracted id_types: %s", id_types)
        return id_types

    except Exception as e:
        log.error("Failed to read or process JSON file: %s", str(e))
        return [{"id": "home", "text": "home"}]

class IDTypeClassifierTool(BaseModel):
    id_type: List[str]


def classify_id_type(payload, graph):
    
    """
    Classifies the id_type based on the user input.

    Args:
        payload (dict): The payload containing user input to classify

    Returns:
        payload: The classified payload with id_type
    """
    id_types_map = {item["id"]: item["text"] for item in extract_id_types_from_json(payload.role)}
    IDTypeClassifierTool.__annotations__['id_type'] = Literal[tuple(id_types_map.keys())]

    # Step 4: Rebuild the model schema to apply the change
    IDTypeClassifierTool.model_rebuild(force=True)
    # Create the prompt using f-string and escape {user_input}
    ID_TYPE_PROMPT = f"""<role>
    You are an intelligent classifier that identifies the most appropriate `id_type` values from a user's query.
    Your job is to choose which `id_type` values from the predefined list best match the query context.

    Available id types:
    {id_types_map.keys()}

    Rules:
    1. Only classify when you're highly confident (above 70%).
    2. Consider synonyms, abbreviations, and common naming variations (e.g., "report" vs "statement").
    3. If multiple id_types are equally relevant, return all of them as a list (e.g., ["ledger_report", "itr_statement"]).
    4. If no strong match exists, return ["other"].
    5. If the query contains question words like "what", "how", "when", "where", "why", or "which", treat it as an informational question and return ["other"].

    Examples:
    - "statement", "report" → ["ledger_report", "itr_statement", "brokerage_report", "profit_loss_report", dp_statement"]
    - "home", "all buttons", "home button", "show initial" → ["home"]
    - "ledger report", "ledger statement" → ["ledger_report"]
    - "DP statement", "dp", "DP" → ["dp_statement"]
    - "itr", "ITR", "ITR Statement" → ["itr_statement"]
    - "brokerage", "brokerage statement", "brokerage report" → ["brokerage_report"]
    - "can you provide me dp statement" → ["other"]
    - "what is my ledger report" → ["other"]
    - "what is DP" → ["other"]
    - "which funds status?" → ["other"]
    - "when available margin" → ["other"]
    - "where is dpid" → ["other"]
    - "how much p&l" → ["other"]
    </role>

    <user_input>
    {{user_input}}
    </user_input>

    <instruction>
    Use the `IDTypeClassifierTool` to classify the user_input strictly.
    Always return a list of matching id_type strings. If no strong match, return ["other"].
    </instruction>
    """




    flow_router_tool = [IDTypeClassifierTool]
    flow_router_model = get_llm_model()

    flow_router_prompt = ChatPromptTemplate.from_messages([
        ("system", ID_TYPE_PROMPT),
        ("human", "user_input: {user_input}"),
    ])

    flow_router_runnable = flow_router_prompt | flow_router_model.bind_tools(flow_router_tool)

    log.info("Starting ID type classification...")
    try:
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
        snapshot_state = graph.get_state(config)
        # if snapshot_state.values.get("inrpt"):
        if len(snapshot_state.tasks)>0 and len(snapshot_state.tasks[0].interrupts)>0:
            log.info("Interrupt detected in the graph state, skipping ID type classification.")
            # If an interrupt is detected, skip classification
            return payload
        flow_type = payload.interaction.type
        user_input = payload.interaction.input.text
        log.info(f"length of input - {len(user_input.split())}")
        if flow_type == "AGENTIC_FLOW" and len(user_input.split()) < 4:
            log.info("Short input detected in agentic flow")
            # Invoke the flow router runnable with the user input
            log.info("Invoking flow router runnable for short input in agentic flow")
            result = flow_router_runnable.invoke( {"user_input": user_input })
            log.info(f"Result from flow router: {result}" )
            # id_type = result.tool_calls[0]['args'].get('id_type', 'other')
            id_type_list = result.tool_calls[0]['args'].get('id_type', [])
            matched_choices = [
                {"id": _id, "text": id_types_map[_id]}
                for _id in id_type_list
                if _id in id_types_map
            ]

            if matched_choices:
                log.info(f"Returning matched choices: {matched_choices}")
                return {
                    "action": "option",
                    "response_text": "Did you mean one of these options?",
                    "available_choices": matched_choices
                }
            else:
                # If classified as 'other', return the payload with id_type set to 'other'
                log.info("Classified as 'other' due to short input in agentic flow")
                return  None
        else:
            log.info("Long input detected or not in deterministic, skipping classification")
            # If the input is long or not in agentic flow, skip classification
            return None
    except Exception as e:
        log.error(f"ID type classification failed: {str(e)}")
        # If classification fails, return the payload unchanged
        return payload