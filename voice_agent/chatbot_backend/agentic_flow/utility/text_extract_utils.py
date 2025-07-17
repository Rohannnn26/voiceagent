

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from agentic_flow.utility import get_llm_model
from monitoring.logger.logger import Logger

# Initialize logger
log = Logger()

# Define the tool schema
class ClientCodeExtractorTool(BaseModel):
    """Extracts client code from a text response."""
    client_code: str = Field(..., description="The extracted client code, e.g., ABC123")

# Build the prompt for the LLM
CLIENT_CODE_PROMPT = """
<role>
You are an expert extraction agent.
Your job is to read the user's response and extract the client code.
A client code is an alphanumeric string like EMUM102915, NAGSYA5, etc.
If no client code is found, return an empty string.
</role>

<instruction>
Use the `ClientCodeExtractorTool` to return the extracted client code.
</instruction>
"""

client_code_prompt = ChatPromptTemplate.from_messages([
    ("system", CLIENT_CODE_PROMPT),
    ("human", "Response: {response}")
])

# Get the LLM model and bind the tool
client_code_tool = [ClientCodeExtractorTool]
llm = get_llm_model()
client_code_runnable: Runnable = client_code_prompt | llm.bind_tools(client_code_tool)

# Define the main function to call the runnable
def extract_client_id_from_message(response: str):
    """
    Uses LLM to extract client code from the response.
    """
    log.info("Starting LLM-based client code extraction...")
    try:
        result = client_code_runnable.invoke({"response": response})
        log.info(f"Client code extraction complete: {result}")
        # result will be a list of tool outputs, pick the first
        return result.tool_calls[0]['args'].get("client_code", "").strip() if result.tool_calls else None
    except Exception as e:
        log.error(f"Client code extraction failed: {str(e)}")
        return None