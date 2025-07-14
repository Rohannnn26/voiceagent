from typing import Literal
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage

from config.config import langfuse
from agentic_flow.utility import get_llm_model
from monitoring.logger.logger import Logger

# Initialize logger
log = Logger()

# This is the ONLY tool schema
class ClassifierTool(BaseModel):
    """Classify the user request into one of the supported agents."""
    classifier: Literal[
        "TradingAgent",
        "ReportAgent",
        "AccountAgent",
        "InformationCentreAgent",
        "FundAgent",
        "DPAgent",
        "Greeting"
        "Other"
    ] = Field(..., description="Agent name that best matches the user's request.")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score for the selected classifier.")
    query: str = Field(..., description="The original user query that is being classified.")

CLSSIFIER_SYSTEM_PROMPT = """<role>
You are a classifier assistant for Motilal Oswal Financial Services LTD.
</role>

<objective>
Classify the user query into one of the predefined agent categories by calling the `classifier` tool.
</objective>

<classifiers>
- TradingAgent: Classify here when the user asks to start or stop online trading access or requests trading activation/deactivation. Typical intent includes enabling or disabling trading services on the account.

- ReportAgent: Use when the user requests financial documents such as:
    - Profit & Loss (P&L) statements
    - Ledger reports
    - Contract notes
    - Sauda details
    - Brokerage reports
    - Tax documents like ITR, STT, TDS
    - Registrar Transfer Agent (RTA) or Digi CMR reports
This agent is for data or report retrieval requests, especially related to investments or compliance.

- AccountAgent: Use for actions or information about account profile or status, such as:
    - Checking or updating account details (email, phone, bank)
    - Reactivating dormant accounts
    - Accessing modification forms
    - Viewing client profile or dashboard
    - Status tracking of any account change
Focus is on account management and personal information updates.

- InformationCentreAgent: Classify queries that ask about:
    - Corporate actions, e.g. IPOs, buybacks, dividends
    - Market research reports
    - FAQs, platform features, policies, how-tos
Use this for informational queries not tied to specific personal data or accounts.

- FundAgent: Use when the query involves fund status, including:
    - Payout or fund transfer tracking
    - Margin availability or penalty
    - Mutual fund order or SIP status
Focus is on fund movement, margin queries, and mutual fund execution.

- DPAgent: Use when the user refers to DP (Depository Participant) services, such as:
    - DP statements
    - Holdings in demat accounts
    - DPID information
    - DIS/DRF status or Digi CMR
Key focus: demat account holdings and related infrastructure (not trading or tax).

- Greeting: Use when the query is a basic greeting or thank you, with no intent to route (e.g., "Hi", "Thanks", "Good morning").

- Other: Use only when none of the above categories apply clearly or the intent is ambiguous or unrelated.
</classifiers>

<instruction>
- Read and understand the user query.
- Call the `classifier` tool with following fields:
  - `classifier`: Choose the most appropriate agent name as a string
  - `confidence_score`: Estimate a confidence score between 0.0 and 1.0.
  - `query`: The original user query as a string.
- Ensure the classifier is accurate and relevant to the user request.
</instruction>
"""


classifier_tool = [ClassifierTool]

log.info("Initializing intent classifier")
model = get_llm_model()
log.info("LLM model loaded for intent classification")

# Assistant prompt template
assistant_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", CLSSIFIER_SYSTEM_PROMPT),
        ("placeholder", "{messages}"),
    ]
)

# Building Runnable object
log.info("Configuring classifier with tools and prompt template")
assistant_runnable = assistant_prompt | model.bind_tools(classifier_tool)
log.info("Intent classifier successfully initialized")

def get_user_intent(user_query, session_id=None, user_id=None):
    """
    Classifies user query intent using the configured LLM with tools.
    
    Args:
        user_query (str): The user message to classify
        
    Returns:
        The classification response from the model
    """
    log.info(f"Processing intent classification for query: {user_query[:50]}...")
    
    try:
        # Create a Langfuse trace for monitoring the intent classification
        with langfuse.start_as_current_span(name="Input Intent Classifier") as span:
            span.update_trace(
            user_id=user_id,  # You may want to add actual user_id if available
            session_id=session_id,      # Add session_id if available
            input={"query": user_query},
            tags=["classifier"]
            )
            
            log.info(f"Invoking classifier with user query: '{user_query}'")
            response = assistant_runnable.invoke(
            {"messages": [HumanMessage(content=user_query)]}
            )
            log.info(f"Classification completed successfully")
            
            span.update_trace(output={"response": response})
            
            return response
    except Exception as e:
        log.error(f"Intent classification failed: {str(e)}")
        raise