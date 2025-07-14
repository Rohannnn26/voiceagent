from pydantic import BaseModel, Field
from typing import Literal
import re

from langchain_core.prompts import ChatPromptTemplate
from agentic_flow.utility import get_llm_model

from monitoring.logger.logger import Logger
# Initialize logger
log = Logger()


FORBIDDEN_MESSAGE = "Message Validation Failed due to unwanted content."
FORBIDDEN_RULES = {
    "REMOVE_API_LINKS": r"^https?:\/\/10\.167\.203\.119\/gw\/api\/cbot(\/.*)?$",
}
BAN_WORDS = [
    "FROM_DATE", "RETURN_TYPE", "TO_DATE", "StatementType", "userId", "DPID", "clientId", "userrole",
    "fromDate", "toDate", "EXCHANGE_SEG", "documentType", "UserId", "ClientId",
    "Role", "PortFolioNo", "refNo", "packetNo", "portfolioNo", "dpId", "orderType", "encclientCode",
    "encSessionNo", "YEAR_Type", "linktype", "startDate", "endDate", "PanOrNumber", "bacode",
    "mobileno", "userid", "clientid", "userRole",
    "botapi/CBot/GetDetails", "botapi/CBot/GetBADetails", "api/CBot/GetDetailsWithMobile",
    "botapi/CBot/GetBADetailsWithMobile", "api/One/ClientDetails", "botapi/One/GetClientCodeByMobileNumber",
    "botapi/One/GetMobileNumberByClientCode", "botapi/One/BranchDetails", "api/One/GetClientWiseDPId",
    "api/One/CordysFundPayoutStatus", "api/One/ContractNote", "api/One/DPStatement", "api/One/ITRStatement",
    "api/One/LedgerStatement", "api/One/STTCertificate", "api/One/DownloadDocument", "api/One/MarginShortage",
    "api/One/ActiveIPO", "api/One/eModificationDetails", "api/One/MutualFundStatement",
    "api/One/DPRequestStatus", "api/One/MarginShortagePenalty", "api/One/ClientView", "api/One/CapitalGainLoss",
    "api/One/SaudaDetails", "api/One/HitPacketStatus", "api/One/SipStatus", "api/One/DisBookRequest",
    "api/One/Hits", "api/One/LedgerBalanceSummary", "api/One/FundPayoutStatus", "api/One/FundsTransfer",
    "api/One/MF_ORDERSTATUS", "api/One/QuickLinks", "api/One/BrokerageDetails", "api/One/CollateralHolding",
    "api/One/EmailAndMobileLinkDetails", "api/One/FundsTransferLink", "api/One/ActiveUser",
    "api/One/MarginFunding", "api/One/SegmentAdditionalLink", "api/One/ClientCMRReport",
    "api/One/GetSaticLinkOrFile", "api/One/StoreRMChangeRequest", "api/One/CheckClientMTFLAS",
    "api/One/GrandFatherGainLossDetailsReport", "api/One/DISDRFStatus", "api/One/ValidClientCode",
    "api/One/AccountStatusReq", "api/One/getSOAMFLink",
    "InformationCentreReactAgent", "ReactAgent", "ReportAgent", "AccountAgent", "FundAgent",
    "TradingAgent", "InformationCentreAgent", "DPAgent",
    "informationcentrereactagent", "INFORMATIONCENTREREACTAGENT", "Informationcentrereactagent",
    "Information Centre React Agent", "reactagent", "REACTAGENT", "Reactagent", "React Agent",
    "reportagent", "REPORTAGENT", "Reportagent", "Report Agent", "accountagent", "ACCOUNTAGENT",
    "Accountagent", "Account Agent", "fundagent", "FUNDAGENT", "Fundagent", "Fund Agent",
    "tradingagent", "TRADINGAGENT", "Tradingagent", "Trading Agent", "informationcentreagent",
    "INFORMATIONCENTREAGENT", "Informationcentreagent", "Information Centre Agent", "dpagent",
    "DPAGENT", "Dpagent", "DP Agent"
]



def get_regex_output_guard(message):
    """
    Check output message against regex patterns for forbidden content.
    Raises ValueError if forbidden patterns are found.
    """
    log.info("Starting Regex output guard...")
    
    # Check for forbidden patterns in the message
    log.info(f"Checking message for forbidden patterns: {message[:50]}...")
    for reason, pattern in FORBIDDEN_RULES.items():
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            log.warning(f"Forbidden pattern detected: Reason: {reason} Value: {match}")
            return f"{FORBIDDEN_MESSAGE} Reason: {reason} Value: {match}"
    
    log.info("Regex guard check completed - no forbidden patterns detected")
    return True

def get_ban_words_guard(message):
    """
    Check output message against a list of banned words.
    Raises ValueError listing all banned words found.
    """
    log.info("Starting Banned words guard...")

    found_words = [word for word in BAN_WORDS if word in message]
    
    if found_words:
        log.warning(f"Banned words detected: {found_words}")
        banned_list_str = ", ".join(f"`{word}`" for word in found_words)
        return f"{FORBIDDEN_MESSAGE} Banned words detected: {banned_list_str}"
    
    log.info("Banned words guard check completed - no banned words detected.")
    return True


# Tool schema
class GroundingValidatorTool(BaseModel):
    """Evaluate the consistency and contextual grounding of response against retrieved context."""
    
    query_response_relevance: Literal["High", "Moderate", "Low"] = Field(...)
    response_chunk_alignment: Literal["Aligned", "Partially Aligned", "Misaligned"] = Field(...)
    issues: str = Field(...)

# Tool + model setup
validator_tool = [GroundingValidatorTool]
validator_model = get_llm_model()

CONTEXT_VALIDATOR_PROMPT = """<role>
You are a contextual grounding evaluator responsible for assessing whether a llm response is relevant and well-grounded in a retrieved knowledge chunk.
</role>

<task>
Evaluate the following:
- How relevant the response is to the retrieved knowledge chunk.
- How well it reflects the retrieved chunk.
</task>

<instruction>
Use `GroundingValidatorTool` to output your structured evaluation.
</instruction>
"""

validator_prompt = ChatPromptTemplate.from_messages([
    ("system", CONTEXT_VALIDATOR_PROMPT),
    ("human", "Response: {response}\n\nRetrieved Chunk: {chunk}")
])

validator_runnable = validator_prompt | validator_model.bind_tools(validator_tool)

def validate_api_response_grounding(response, chunk, session_id=None, user_id=None):
    """
    Evaluates contextual grounding between response, and retrieved chunk.
    """
    
    try:
        log.info("Validating API Response grounding ...")

        result = validator_runnable.invoke({
            "response": response,
            "chunk": chunk
        })
        log.info("API Response Grounding validation complete.")
        return result
    except Exception as e:
        log.error(f"API Response grounding validation failed: {str(e)}")
        raise