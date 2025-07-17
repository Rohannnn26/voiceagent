import os
import logging
import asyncio, base64, datetime, textwrap, bs4, requests
from zoneinfo import ZoneInfo
from faq_agent.information_center_agent import faq_knowledge_base

from logger import logger

# Optional: Only if not configured globally elsewhere
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

# ── Tool: Get Time ────────────────────────────
def get_time(city: str, status_callback=None, **kwargs) -> dict:
    """Return IST time, regardless of requested city (demo)."""
    logger.info(f"[get_time] Arguments received - city: '{city}', kwargs: {kwargs}")
    
    now_ist = datetime.datetime.now(ZoneInfo("Asia/Kolkata"))
    result = {"time": f"It is {now_ist:%H:%M} IST in {city}."}
    
    logger.info(f"[get_time] Generated time result: {result}")
    return result

# ── Tool: Chatbot Backend Integration ─────────────────
async def query_chatbot_backend(question: str, status_callback=None, **kwargs) -> dict:
    """
    Query the LangGraph chatbot backend for complex financial questions,
    account details, reports, and other advanced queries that require
    the full agentic workflow.
    """
    logger.info(f"[query_chatbot_backend] Arguments received - question: '{question}', kwargs: {kwargs}")
    
    try:
        from chat_wrapper import run_chat
        logger.info(f"[query_chatbot_backend] Calling backend with question: '{question}'")
        response = await run_chat(question)
        
        # Log full response details
        logger.info(f"[query_chatbot_backend] Backend returned {len(response)} characters")
        logger.info(f"[query_chatbot_backend] Full backend response: {response}")
        
        result = {"response": response}
        logger.info(f"[query_chatbot_backend] Returning result: {result}")
        return result
    except Exception as e:
        error_msg = f"Backend query failed: {e}"
        logger.error(f"[query_chatbot_backend] Error occurred: {error_msg}")
        logger.error(f"[query_chatbot_backend] Exception details: {type(e).__name__}: {str(e)}")
        return {"error": error_msg}

# ── Tool Schemas ─────────────────────────────
FUNCTION_SCHEMAS = [
    {
        "type": "function",
        "name": "get_time",
        "description": "Get the current time in a city.",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"]
        },
    },
    {
    "type": "function",
    "name": "faq_knowledge_base",
    "description": """
        Search Motilal Oswal's comprehensive FAQ knowledge base for general policies, procedures, and regulatory information.

        **USE THIS TOOL FOR:**
        - General policy questions and procedures
        - Regulatory and compliance information (SEBI, KRA, NSDL guidelines)
        - Standard processes and documentation requirements
        - Platform features and functionality explanations
        - Financial terms and definitions
        - Common troubleshooting issues

        **TYPICAL EXAMPLES:**
        - "What is SPEED-e of NSDL?" - Regulatory process queries
        - "Are existing client details mandatory on modification forms?" - Documentation requirements  
        - "Can I open demat account if trading account exists?" - Account opening policies
        - "Do I need documents if KRA registered?" - Compliance requirements
        - "What is Physical Settlement in EQ-Derivatives?" - Trading mechanism explanations
        - "Why does session get expired?" - Platform functionality issues
        - "What are the charges for..." - Fee structure queries
        - "How to reset password?" - General platform guidance
        - "What documents needed for account opening?" - Standard procedures

        **DON'T USE FOR:**
        - Personalized account information (use backend tool instead)
        - Specific reports or statements (use backend tool instead)
        - Account modifications or transactions (use backend tool instead)
        """,
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "Customer's general question about policies, procedures, or regulations"
            }
        },
        "required": ["question"]
    },
},

    {
        "type": "function",
        "name": "query_chatbot_backend",
        "description": """
        Connect to Motilal Oswal's comprehensive backend system with 6 specialized departments for personalized client services:

        🏢 **SPECIALIZED DEPARTMENTS AVAILABLE:**

        📊 **REPORTS & STATEMENTS DEPARTMENT:**
        - Financial reports: P&L statements, ledger reports, brokerage statements
        - Trade documents: Contract notes, sauda details, trading history
        - Tax documents: ITR reports, STT certificates, TDS certificates  
        - Mutual fund reports: RTA statements, order status
        - Digital reports: DIGI CMR (Client Master Report)

        👤 **ACCOUNT SERVICES DEPARTMENT:**
        - Client profile and dashboard information
        - Account status and modification tracking
        - Branch details and contact information
        - Dormant account reactivation assistance
        - Profile updates: email, phone, address, bank details, nominee changes
        - Account opening forms for Individual/HUF/NRI/Partnership/Corporate/Trust

        💰 **FUNDS & MARGIN DEPARTMENT:**
        - Fund transfer status and payout tracking
        - Margin availability and shortage penalty reports
        - Mutual fund order status and SIP processing
        - Payment-related queries and transactions

        📈 **TRADING DESK:**
        - Online trading activation and deactivation
        - Trading account management and settings
        - Trading-related technical support

        🏦 **DP (DEPOSITORY PARTICIPANT) SERVICES:**
        - DP statements and holdings reports
        - DPID (Depository Participant ID) information
        - DIS/DRF status checking
        - Advisor change requests
        - Demat account operations

        📰 **INFORMATION & RESEARCH CENTER:**
        - Corporate actions and market events
        - IPO information and investment opportunities  
        - Market research reports and analysis
        - General platform guidance and troubleshooting

        **USE THIS TOOL FOR:**
        - Any personalized account information or transactions
        - Report generation and downloads
        - Account modifications and updates
        - Trading and investment services
        - Market research and corporate action updates
        - Complex queries requiring backend system access

        **EXAMPLES:**
        "Show my account balance", "Generate P&L report", "Check trading status", 
        "Update my phone number", "IPO applications", "Margin shortfall details",
        "DP holdings report", "Corporate action updates"
        """,
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The client's specific question or request that requires backend system access"
                }
            },
            "required": ["question"]
        },
    }

]

# ── Tool Dispatcher ──────────────────────────
TOOLS = {
    "get_time": get_time,
    "faq_knowledge_base": faq_knowledge_base,
    "query_chatbot_backend": query_chatbot_backend,
}
