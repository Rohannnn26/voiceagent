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

# Report agent output schema
# class AgentOutput(BaseModel):
#     """
#     STRUCTURED SCHEMA FOR AI ASSISTANT RESPONSES — USED TO DRIVE UI RENDERING AND DIALOG FLOW CONTROL.

#     FIELDS:
#         message (str): A polished, user-facing response from the assistant.
#             - If a Markdown link is included (e.g., [View Report](https://...)), only the link text should be displayed to the user.
#             - If no link is included, display the full message content written in natural, friendly language.
#             - The assistant will never expose technical details, raw payloads, or internal API logic.
#             - The tone is always professional, clear, and helpful — tailored for a financial services customer environment.

#         status (Literal): Indicates the assistant's current interaction stage:

#             - "awaiting_clarification": Assistant is asking the user to provide missing or unclear input.
#             - "awaiting_confirmation": All inputs are ready, and the assistant is asking for final confirmation before proceeding.
#             - "result": Final message after performing the requested action (e.g., returning a report link or outcome).
#             - "out_of_scope": The assistant could not match the user’s request to any known operation.
#     """

#     message: str = Field(
#         ...,
#         description=(
#             "Polished, user-facing message written in a professional and friendly tone. "
#             "If a Markdown link is present (e.g., [Download Report](https://...)), show only the link to the user. "
#             "If no link is present, render the full text response. "
#             "Message content avoids all technical, backend, or system-specific details — it focuses on natural, helpful communication."
#         )
#     )

#     status: Literal[
#         "awaiting_clarification",
#         "awaiting_confirmation",
#         "result",
#         "out_of_scope"
#     ] = Field(
#         ...,
#         description=(
#             "'awaiting_clarification': Missing required input(s); assistant is prompting the user.\n"
#             "'awaiting_confirmation': All details are collected; assistant is confirming intent.\n"
#             "'result': Final outcome message, including any returned data or report links.\n"
#             "'out_of_scope': Request was not mapped to any supported capability or operation."
#         )
#     )

# class AgentOutput(BaseModel):
#     """
#     You are a financial services assistant that provides responses using a structured output format.
#     When responding to user queries, you must format your response according to the AgentOutput schema which controls 
#     how the UI displays your messages and manages conversation flow.

#     Always adhere to these guidelines:

#     1. Structure each response with two components:
#         - message: A clear, professional, and friendly response written in natural language
#         - status: The appropriate conversation stage from the allowed options
    
#     2. Status field requirements:
#         - Use "awaiting_clarification" when you need more information to proceed
#         - Use "awaiting_confirmation" when all inputs are ready and you need final approval
#         - Use "result" when providing a final outcome or report
#         - Use "out_of_scope" only when the request doesn't match any supported capability
    
#     3. Message formatting rules:
#         - Write in a warm, professional tone appropriate for financial services
#         - Present information in well-organized, readable structures with proper spacing
#         - Use plain language that non-technical customers can understand
#         - Never expose API parameters, technical notation, or system details
#         - Replace technical symbols in api parameters (|, &) with natural words ("or", "and")
#         - Use complete sentences and natural descriptive labels
#         - For report links, use standard Markdown format: [View Report](https://link)
    
#     4. When awaiting clarification:
#         - Clearly explain what information is needed and why
#         - Provide examples where helpful
#         - Present options in user-friendly formats and readable structures with proper spacing
    
#     """

#     message: str = Field(
#         ...,
#         description=(
#             "Polished, user-facing message written in a professional and friendly tone. "
#             "If a Markdown link is present (e.g., [Download Report](https://...)), show only the link to the user. "
#             "If no link is present, render the full text response. "
#             "Message content avoids all technical, backend, or system-specific details — it focuses on natural, helpful communication."
#         )
#     )

#     status: Literal[
#         "awaiting_clarification",
#         "awaiting_confirmation",
#         "result",
#         "out_of_scope"
#     ] = Field(
#         ...,
#         description=(
#         " 'awaiting_clarification' : when you need more information to proceed \n"
#         " 'awaiting_confirmation' :  when all inputs are ready and you need final approval \n"
#         " 'result' : when providing a final outcome or report \n"
#         " 'out_of_scope' : only when the request doesn't match any supported capability " 
#         )
#     )

class AskBackToUser(BaseModel):
    """
    Tool to get clarity / Confirmation from Customer.
    """
    
    interrupt_message: str = Field(
        description="Message to show to the user when requesting input or confirmation. Since the response is viewed on a mobile screen, it should be concise and straight to the point."
    )

class AgentOutput(BaseModel):
    """A tool to mark the current task as completed and/or to escalate control of the dialog to the supervisor agent,
    who can re-route the dialog based on the user's need."""

    message: str = Field(
        ...,
        description="""
            REPLY TO THE CUSTOMER IN MARKDOWN FORMAT.
            Organize the information in a logical, easy-to-follow structure.
            Avoid technical terminology such as API names or parameter names.
            Prioritize mobile readability, as it is an important consideration.
            For HTML content, especially tables:
            - Convert simple HTML elements to markdown (e.g., <br> to newlines, <h1> to #).
            - For complex HTML tables, either convert them to markdown tables using the | syntax or, if too complex, simplify the structure for clarity.
            Replace HTML escape characters with appropriate symbols, and ensure all content remains readable—even if formatting isn't perfect.
        """
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

