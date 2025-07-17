
from langchain_core.runnables import Runnable, RunnableConfig
# from langgraph.types import interrupt
from agentic_flow.utility.llm_models import pre_model_hook
from app.schemas.request_models import SupervisorState, AgentOutput
from agentic_flow.prompts.primary_assistant_prompt import create_prompt_template
from agentic_flow.prompts.prompts import REACT_SYSTEM_PROMPT_TEMPLATE

from agentic_flow.tools.react_tool import react_tools

from agentic_flow.utility import ( 
                                    read_and_pretty_print_json, 
                                    today_date,
                                    get_indian_financial_year,
                                    inject_tool_message 
                                )

import os
from config.config import REPORT_OPENAPI_SCHEMA_PATH
from monitoring.logger.logger import Logger

log = Logger()

def get_runnable_react(model, api_schema_path, static_data_path=None) -> Runnable:
    """
    Creates a runnable React agent configured with API schema.
    This function initializes a React agent by creating a prompt with the provided API schema
    and binding React tools to the specified model.
    Args:
        model: The language model to use for the React agent.
        api_schema_path (str): Path to the JSON file containing the API schema.
    Returns:
        Runnable: A runnable React agent configured with the API schema and tools.
    """
    agent_name = os.path.basename(api_schema_path).replace(".json", "").strip()
    log.info(f"React agent for {agent_name} Creating...")

    # Load and pretty print the API schema
    apispec = read_and_pretty_print_json(api_schema_path)
    static_data=""
    if static_data_path:
        static_data = read_and_pretty_print_json(static_data_path)
        static_data ="\n use following static context to address customer's query if applicable. \n"+ static_data
    log.info(f"API Specification loaded.")
    # Create the React agent prompt with the API specification
    react_agent_prompt = create_prompt_template(REACT_SYSTEM_PROMPT_TEMPLATE, apispec, static_data)
    
    # Building Runnable object
    react_runnable = react_agent_prompt | model.bind_tools(react_tools)
    log.info(f"React agent runnable for {agent_name} created successfully.")
    return react_runnable

class ReactAgent:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: SupervisorState, config: RunnableConfig):
        MAX_RETRIES = 5
        retry_count = 0
        while retry_count < MAX_RETRIES:
            log.info("react agent initiated...")
            inject_tool_message(state)
            payload = state.get("payload", {})
            payload = payload.dict()
            # log.info(f"Payload received: {payload}")
            # Ensure payload has the required attributes
            client_id = payload.get("client_id", None)
            log.info(f"Client ID from payload: {client_id}")
            # if client_id is None or client_id == "":
            #     log.error("Client ID is missing in the payload.")
            #     client_id = interrupt("Please provide your Client ID (Client Code).")
            #     log.info(f"Client ID: {client_id}") 

            # Get required data
            fy_start_date, fy_end_date = get_indian_financial_year()
            trimmed_messages = pre_model_hook(state.get("messages", []))
            # log.info(f"Trimmed messages: {trimmed_messages}")

            
            inputs= { 
                        "today_date": today_date,
                        "client_id": client_id,
                        "role": payload.get("role", "client"),
                        "fy_start_date": fy_start_date,
                        "fy_end_date": fy_end_date,
                        "messages": trimmed_messages,
                    }
            # log.info(f"messages: {inputs['messages']}")
            # Invoke the React agent with the inputs
            log.info("Invoking React agent with inputs...")
            result = self.runnable.invoke(inputs)
            log.info("React agent invoked successfully.")
            # Log the result from the React agent
            # log.info(f"Result from React agent: {result}")
            # Check if the result contains tool calls or content
            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                retry_count += 1
                log.info(f"Tool not invoked. Retry count: {retry_count}")
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
                log.info("Tool not invoke.")
            else:
                log.info("Assistance Break.")
                break

        log.info("react agent completed.")
        if retry_count >= MAX_RETRIES:
            response = {
                "status": "Failed",
                "message": "I sincerely apologize for not able to fulfill your request.",
                "action": "result"
            }
        else:
            response = {
                "status": result.tool_calls[0]["args"].get("status", "Success") if result.tool_calls else "Success",
                "message": result.tool_calls[0]["args"].get("message", "") if result.tool_calls else result.content or "",
                "action": "result"
            }

        return {
            "messages": result,
            "response": response
        }

