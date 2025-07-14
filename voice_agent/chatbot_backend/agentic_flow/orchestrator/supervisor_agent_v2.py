
from langchain_core.runnables import Runnable, RunnableConfig
from agentic_flow.utility.llm_models import pre_model_hook
from app.schemas.request_models import SupervisorState, AgentOutput
from agentic_flow.prompts.primary_assistant_prompt import assistant_prompt
from agentic_flow.tools.assistant_tool import agents_tools
from monitoring.logger.logger import Logger

# Initialize logger
log = Logger()


class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: SupervisorState, config: RunnableConfig):
        trimmed_messages = pre_model_hook(state.get("messages",[]))
        inputs= {
            "messages" : trimmed_messages    
        }
        log.info(f"Trimmed messages: {trimmed_messages}")
        while True:
            log.info("Assistance started..")
            result = self.runnable.invoke(inputs)

            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
                log.info("Tool not invoke.")
            else:
                log.info("Assistance Break.")
                break

        log.info("Assitance completed.")

        message_str = "Hello! How can I assist you today?"

        if isinstance(result.content, list):
            message_str = str(result.content[0].get("text", ""))
        else:
            message_str = str(result.content)

        # Default values
        assistance_response = AgentOutput(
            message=message_str,
            status="result"
        )

        return {
            **state,
            "response": assistance_response.dict(),
            "messages": result
        }

        # return {"messages": result}

# build Runnable object assistance
def get_runnable_assistance(model):
    
    # Building Runnable object
    assistant_runnable = assistant_prompt | model.bind_tools(agents_tools)

    return assistant_runnable
