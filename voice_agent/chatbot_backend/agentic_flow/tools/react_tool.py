import json
from typing import Dict, Any, Annotated, Optional
from langchain_community.utilities.requests import TextRequestsWrapper
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from langchain_community.retrievers.bedrock import AmazonKnowledgeBasesRetriever
import traceback

from app.schemas.request_models import AgentOutput, AskBackToUser
from config.config import SYSTEM_PARAMS_MAPPER_PATH
from agentic_flow.utility import load_json_file
from config.config import (
    AWS_KB_ID,
    AWS_KB_RETRIVAL_CONFIG,
    AWS_REGION,
    AWS_GUARDRAIL_CONFIG
)
from monitoring.logger.logger import Logger

# Initialize logger
log = Logger()

@tool
def request_post(text: str, state: Annotated[dict, InjectedState]):
    """
    Use this tool to make a POST request to a specified API endpoint. 
    Input should be a JSON string with 'url' and 'data' keys.
    The 'url' should be a string, and 'data' should be a dictionary of key-value pairs to POST.
    """
    log.info("Request POST tool initiated...")

    def _get_post_tool_data(url: str, state: dict):
        """Extracts the necessary data for POST requests from the state."""
        system_params_mapper = load_json_file(SYSTEM_PARAMS_MAPPER_PATH)

        if not system_params_mapper:
            log.error("Failed to load system parameters mapper from JSON file.")
            return {}, {}

        if url not in system_params_mapper:
            log.error(f"URL {url} not found in system parameters mapper.")
            return {}, {}

        payload = state.get("payload").dict()
        log.info(f"Payload received: {payload}")
        if not payload:
            log.error("Payload is empty or not provided in the state.")
            return {}, {}

        system_params = system_params_mapper.get(url, {})
        body = {}

        for key, value in system_params.items():
            attribute = payload.get(key)
            if attribute is None:
                log.warning(f"Attribute '{key}' not found in payload: {payload}")
            else:
                log.info(f"Extracted {key} from payload: {attribute}")
                body[value] = attribute

        headers = {
            "sessionid": payload.get("session_id", ""),
            "token": payload.get("token", ""),
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json"
        }

        return headers, body

    def _parse_input(text: str) -> Dict[str, Any]:
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            log.error(f"Failed to parse input JSON: {e}")
            return {}

    def _clean_url(url: str) -> str:
        return url.strip("\"'")

    data = _parse_input(text)
    if not data or "url" not in data or "data" not in data:
        log.error("Input JSON must contain 'url' and 'data' keys.")
        return "Invalid input format"

    url = _clean_url(data["url"])
    if not url:
        log.error("URL is empty or invalid.")
        return "Invalid URL"

    headers, body = _get_post_tool_data(url, state)
    if not headers or not body:
        log.error("Failed to construct headers or body for POST request.")
        return "Error preparing request data"

    if not isinstance(data["data"], dict):
        log.error("'data' field in input must be a dictionary.")
        return "Invalid data field"

    data["data"].update(body)
    log.info(f"Making POST request to {url} with headers: {headers} and body: {data['data']}")

    wrapper = TextRequestsWrapper(headers=headers)
    response = wrapper.post(url, data["data"])

    return response

@tool
def faq_knowledge_base(question: str) -> str:
    """
    Retrieve relevant information from the FAQ knowledge base.
    
    This tool searches the AWS knowledge base for answers about wealth management, stock market trading,
    financial regulations, account procedures, and platform features. Use it for questions about
    financial policies, trading rules, and account management.
    
    TYPICAL FAQ EXAMPLES:
    - "What is SPEED-e of NSDL?"
    - "Are existing client details mandatory to mention on given modification form?"
    - "Can a demat account be opened if a trading or commodity account exists?"
    - "Do i need to give documents if I am KRA registered?"
    - "What is Physical Settlement in EQ-Derivatives?"
    - "Why does the session get expired?"
    
    Args:
        question (str): User's natural language question about financial processes or policies.
    
    Returns:
        str: Relevant information from the knowledge base or a fallback message.
    """
    try:
        retriever = AmazonKnowledgeBasesRetriever(
            knowledge_base_id=AWS_KB_ID,
            retrieval_config=AWS_KB_RETRIVAL_CONFIG,
            region_name=AWS_REGION,
        )
        log.info("FAQ retrieval tool initialized with AWS Knowledge Base")

        log.debug(f"Retrieving FAQ context for question: {question}")
        docs = retriever.get_relevant_documents(question)
        
        if not docs:
            log.warning("No relevant FAQ content found for the question")
            return "I couldn't find a specific answer to your question in our FAQ database. Please try rephrasing your question or ask something more specific about our financial services or policies."

        log.info(f"Retrieved {len(docs)} relevant FAQ documents")
        return "\n\n".join([doc.page_content for doc in docs])
    
    except Exception as e:
        log.error(f"Error in faq_knowledge_base tool: {str(e)}")
        log.error(traceback.format_exc())
        return "I encountered an issue while searching our FAQ database. Please try again later or contact support if the problem persists."


# Initialize basic tools at module level
log.info("Initializing basic tools...")

# Create a list of basic tools
react_tools = [request_post, AskBackToUser, AgentOutput]

information_centre_tools = [faq_knowledge_base, request_post, AskBackToUser, AgentOutput]