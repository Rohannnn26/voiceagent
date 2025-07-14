from pydantic import BaseModel, Field
from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from agentic_flow.utility import get_llm_model
from monitoring.logger.logger import Logger
# Initialize logger
log = Logger()

class GroundingValidatorTool(BaseModel):
    """Evaluate the consistency and contextual grounding of query-response pair."""
    
    query_response_relevance: Literal["High", "Moderate", "Low"] = Field(
        ..., description="Semantic match between original user query and chatbot response."
    )
    response_chunk_alignment: Literal["Aligned", "Partially Aligned", "Misaligned"] = Field(
        ..., description="Does the response reflect and rely on the retrieved context chunk accurately?"
    )
    dialogue_continuity: Literal["Coherent", "Partially Coherent", "Incoherent"] = Field(
        ..., description="Is the response logically coherent with the previous user messages?"
    )
    issues: str = Field(
        ..., description="Brief explanation of any mismatch, incoherence, or hallucination identified."
    )

CONTEXT_VALIDATOR_PROMPT = """<role>
You are a contextual grounding evaluator responsible for ensuring that AI chatbot responses are accurate, relevant, and coherent.
</role>

<task>
Given the original user query, a retrieved context chunk (used as knowledge), and the AI's generated response, evaluate:
1. Whether the response directly answers the user query.
2. Whether the response content is grounded in the retrieved chunk.
3. Whether the response fits within the dialogue flow (if part of a multi-turn conversation).
</task>

<criteria>
- query_response_relevance: "High" if the response directly and fully answers the user query; "Moderate" if partial or vague; "Low" if irrelevant.
- response_chunk_alignment: "Aligned" if the response clearly uses information from the chunk; "Partially Aligned" if only loosely connected; "Misaligned" if hallucinated or off-topic.
- dialogue_continuity: "Coherent" if it logically follows previous messages; "Partially Coherent" if somewhat related but not smooth; "Incoherent" if disjointed.
- issues: Provide a short diagnostic comment highlighting any problem (e.g. hallucination, missing info, vague answer).
</criteria>

<instruction>
Use the `GroundingValidatorTool` to output the evaluation.
</instruction>
"""

validator_tool = [GroundingValidatorTool]

# Load model (your existing function)
validator_model = get_llm_model()

# Create prompt template
validator_prompt = ChatPromptTemplate.from_messages([
    ("system", CONTEXT_VALIDATOR_PROMPT),
    ("human", "Query: {query}\n\nResponse: {response}\n\nRetrieved Chunk: {chunk}\n\nPrevious Dialogue (if any): {dialogue}")
])

# Bind tool
validator_runnable = validator_prompt | validator_model.bind_tools(validator_tool)

def validate_contextual_grounding(query, response, chunk, dialogue_history="", session_id=None, user_id=None):
    """
    Evaluates contextual grounding between query, response, and retrieved chunk.
    """
    
    try:
        log.info("Validating grounding for chatbot response...")

        result = validator_runnable.invoke({
            "query": query,
            "response": response,
            "chunk": chunk,
            "dialogue": dialogue_history
        })
        log.info("Grounding validation complete")
        return result
    except Exception as e:
        log.error(f"Contextual grounding validation failed: {str(e)}")
        raise
