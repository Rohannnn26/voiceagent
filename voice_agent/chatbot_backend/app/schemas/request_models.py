# app/schemas/request_models.py

from typing import Optional, List, Dict, Any, Literal, TypedDict, Annotated
from langgraph.graph.message import AnyMessage, add_messages
from pydantic import BaseModel, Field

class Interaction(BaseModel):
    click_id: Optional[str] = Field(None, description="ID of the clicked element")
    input_text: Optional[str] = Field(None, description="Text input by the user")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Extra contextual info")
    
    class Config:
        extra = "allow"  # Allow extra keys

class InputData(BaseModel):
    text: Optional[str]  # text can be None
    id: Optional[str] = None  # id is optional and defaults to None
    from_date: Optional[str] = None  # from_date is optional and defaults to None
    to_date: Optional[str] = None  # to_date is optional and defaults to None

class Metadata(BaseModel):
    source: Optional[str] = "web"  # Defaults to "web" if not provided

class InteractionV2(BaseModel):
    type: Literal["AGENTIC_FLOW", "DETERMINISTIC_FLOW"]  # Only these two values are valid
    attachement: Optional[str] = ""  # attachement is optional, defaults to an empty string
    input: InputData  # input is required and of type InputData
    metadata: Optional[Metadata] = Metadata()  # metadata is optional and defaults to Metadata()
    request_id: Optional[str] = "" # only for each complete queation answer

    class Config:
        extra = "allow"  # Allow extra fields that are not defined in the schema

# Payload Schema
class Payload(BaseModel):
    user_id: str  # user_id is mandatory
    session_id: str  # session_id is mandatory
    client_id: Optional[str]  # client_id is optional
    role: str  # role is mandatory
    token: str  # token is mandatory
    interaction: InteractionV2  # interaction is required and of type InteractionV2

    class Config:
        extra = "allow"  # Allow extra fields that are not defined in the schema

# Router agent structure output schema
class AgentRouterSchema(BaseModel):
    agent_name: str

# FAQ agent structure output schema
class FAQResponseSchema(BaseModel):
    answer: str = Field(..., description="The assistant's natural language response based only on the FAQ data")
    confidence: Literal["High", "Medium", "Low"] = Field(..., description="The confidence level of the response")
    source_ids: List[str] = Field(..., description="List of source document identifiers used to generate the answer")


class AskBackToUser(BaseModel):
    """
    Tool to ask the customer for clarification or confirmation.

    Used when the agent needs more information from the customer
    to proceed confidently with the conversation.

    The message must be written in markdown and be short, polite, and mobile-friendly.
    """

    interrupt_message: str = Field(
        ...,
        title="Markdown-formatted ask-back message",
        description=(
            "Customer-facing message asking for clarification or confirmation.\n"
            "- Must be in **markdown format** (use markdown like bold, lists, newlines).\n"
            "- Keep it concise, friendly, and clear for mobile screens.\n"
            "Focus on a direct, polite question to the user."
        ),
        example="**Could you please clarify** which product you're referring to?"
    )

class AgentOutput(BaseModel):
    """A tool to mark the current task as completed and/or to escalate control of the dialog
    to the supervisor agent, who can re-route the dialog based on the user's need.
    
    Contains:
    - message: Customer-facing reply in markdown format.
    - status: Control decision signal (fulfilled or escalation)."""

    message: str = Field(
        ...,
        title="Customer-facing reply (markdown)",
        description=(
            "REPLY TO THE CUSTOMER IN MARKDOWN FORMAT.\n"
            "- Organize the information clearly and logically.\n"
            "- Use plain language; avoid technical jargon, API names, or parameter names.\n"
            "- Prioritize readability on mobile screens.\n"
            "- Format using basic markdown (e.g., bold, lists, newlines).\n"
            "The message must NOT include HTML, raw JSON, or system/internal terms."
        )
    )

    status: Literal[
        "result",
        "out_of_scope"
    ] = Field(
        ...,
        description=(
        "result: Only When agent delivers what customer needed, or if it errors out and connot be proceessed "
        "out_of_scope: When agent escalates request to supervisor explicity states that the request is out of scope " 
        )
    )

# langgraph State schema
class SupervisorState(TypedDict, total=False):
    payload: Payload
    messages: Annotated[List[AnyMessage], add_messages]
    agent_name: str
    response: AgentOutput

