from pydantic import BaseModel, Field
from typing import Literal
import re

from langchain_core.prompts import ChatPromptTemplate
from agentic_flow.utility import get_llm_model

from monitoring.logger.logger import Logger
from config.config import BASE_URL_CONFIG
# Initialize logger
log = Logger()


FORBIDDEN_MESSAGE = "You are disclosing technical details about APIs & their parameter, this poses security risk."
FORBIDDEN_RULES = {
    "REMOVE_API_LINKS": r"(http|https)?://10\.167\.203\.119/gw/api/cbot(?:/.*)?",
    "REMOVE_API_URL": BASE_URL_CONFIG,
    "REMOVE_SENSITIVE_ENDPOINTS": r"(?:/.*)?(?:/api/cbot/|/botapi/CBot/|gw/api/cbot)"
}
BAN_WORDS = [
    "FROM_DATE", "RETURN_TYPE", "TO_DATE", "StatementType", "userId", "DPID", "clientId", "userrole",
    "fromDate", "toDate", "EXCHANGE_SEG", "documentType", "UserId", "ClientId",
    "Role", "PortFolioNo", "refNo", "packetNo", "portfolioNo", "dpId", "orderType", "encclientCode",
    "encSessionNo", "YEAR_Type", "linktype", "startDate", "endDate", "PanOrNumber", "bacode",
    "mobileno", "userid", "clientid", "userRole","botapi/CBot/GetDetails",  "api/cbot/ClientDetails", "botapi/cbot/GetMobileNumberByClientCode", "botapi/cbot/BranchDetails", "api/cbot/GetClientWiseDPId",
    "api/cbot/CordysFundPayoutStatus", "api/cbot/ContractNote", "api/cbot/DPStatement", "api/cbot/ITRStatement",
    "api/cbot/LedgerStatement", "api/cbot/STTCertificate", "api/cbot/DownloadDocument", "api/cbot/MarginShortage",
    "api/cbot/ActiveIPO", "api/cbot/eModificationDetails", "api/cbot/MutualFundStatement",
    "api/cbot/DPRequestStatus", "api/cbot/MarginShortagePenalty", "api/cbot/ClientView", "api/cbot/capitalgainLoss",
    "api/cbot/SaudaDetails", "api/cbot/HitPacketStatus", "api/cbot/SipStatus", "api/cbot/DisBookRequest",
    "api/cbot/Hits", "api/cbot/LedgerBalanceSummary", "api/cbot/FundPayoutStatus", "api/cbot/FundsTransfer",
    "api/cbot/MF_ORDERSTATUS", "api/cbot/QuickLinks", "api/cbot/BrokerageDetails", "api/cbot/CollateralHolding",
    "api/cbot/EmailAndMobileLinkDetails", "api/cbot/FundsTransferLink", "api/cbot/ActiveUser",
    "api/cbot/MarginFunding", "api/cbot/SegmentAdditionalLink", "api/cbot/ClientCMRReport",
    "api/cbot/GetSaticLinkOrFile", "api/cbot/StoreRMChangeRequest", "api/cbot/CheckClientMTFLAS",
    "api/cbot/GrandFatherGainLossDetailsReport", "api/cbot/DISDRFStatus", "api/cbot/ValidClientCode",
    "api/cbot/AccountStatusReq", "api/cbot/getSOAMFLink",
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
            return f"{FORBIDDEN_MESSAGE}"
    
    log.info("Regex guard check completed - no forbidden patterns detected")
    return True

def get_ban_words_guard(message):
    """
    Check output message against a list of banned words.
    Raises ValueError listing all banned words found.
    """
    log.info("Starting Banned words guard...")
    lowered_banned_words = set([word.lower() for word in BAN_WORDS])
    lowered_message = message.lower()
    found_words = [word for word in lowered_banned_words if word in lowered_message]
    if found_words:
        log.warning(f"Banned words detected: {found_words}")
        banned_list_str = ", ".join(f"`{word}`" for word in found_words)
        return f"{FORBIDDEN_MESSAGE}"
    
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