from pydantic import BaseModel, Field
from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from agentic_flow.utility import get_llm_model  # Your existing utility

# The code snippet `from monitoring.logger.logger import Logger` is importing the `Logger` class from
# the `logger` module within the `monitoring.logger` package.
from monitoring.logger.logger import Logger
# Initialize logger
log = Logger()

class IntentGuardTool(BaseModel):
    """Ensure the response contains only allowed message types: greeting, thanks, or apology for not knowing."""
    
    intent_type: Literal["Greeting", "ThankYou", "Apology", "Other"] = Field(
        ..., description="Classify the AI response as Greeting, ThankYou, Apology for not answering, or Other."
    )
    reason: str = Field(
        ..., description="Explain briefly why the message was classified this way."
    )

INTENT_GUARD_PROMPT = """<role>
You are a strict output validator. Your job is to check whether the AI's response is strictly one of the following:
1. A greeting (e.g., Hello, Hi, Good day).
2. A thank you message (e.g., Thanks for reaching out, Thank you!).
3. An apology for not being able to answer a question (e.g., I'm sorry, I don’t know that, I’m unable to help with that).
If the message contains **anything else** — such as general knowledge, follow-up questions, or explanations — classify it as "Other".
</role>

<instruction>
Use the `IntentGuardTool` to classify the response strictly.
</instruction>
"""

intent_guard_tool = [IntentGuardTool]
intent_guard_model = get_llm_model()

intent_guard_prompt = ChatPromptTemplate.from_messages([
    ("system", INTENT_GUARD_PROMPT),
    ("human", "Response: {response}")
])

intent_guard_runnable = intent_guard_prompt | intent_guard_model.bind_tools(intent_guard_tool)

def guard_simple_response(response, session_id=None, user_id=None):
    """
    Validates the response to ensure it contains only allowed message types.
    """
    log.info("Starting intent guard check...")
    try:
        log.info("Checking response intent...")

        result = intent_guard_runnable.invoke({
            "response": response
        })
        log.info("Intent guard check complete")
        # log.info(f"Intent guard result: {result}")

        return result
    except Exception as e:
        log.error(f"Intent guard failed: {str(e)}")
        raise
