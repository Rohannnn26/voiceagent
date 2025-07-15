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
    "description": (
                """Search and return answers from Motilal Oswal's internal FAQ knowledge base
                about wealth management, trading, demat procedures, regulations, and account-related issues.

                This tool searches the AWS knowledge base for answers about wealth management, stock market trading,
                financial regulations, account procedures, and platform features. Use it for questions about
                financial policies, trading rules, and account management.

                TYPICAL FAQ EXAMPLES:
                - What is SPEED-e of NSDL?
                - Are existing client details mandatory to mention on given modification form?
                - Can a demat account be opened if a trading or commodity account exists?
                - Do I need to give documents if I am KRA registered?
                - What is Physical Settlement in EQ-Derivatives?
                - Why does the session get expired?
                """
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "Customer's question about financial services or policies"
            }
        },
        "required": ["question"]
    },
},

    {
        "type": "function",
        "name": "query_chatbot_backend",
        "description": ("""
            "Query the advanced chatbot backend for complex financial questions, account details, "
            "trading information, reports, portfolio analysis, and other sophisticated queries that "
            "require the full agentic workflow with access to financial systems and databases. "
            "Use this tool for questions about account details, trading history, portfolio reports, "
            "IPO information, ledger queries, and other complex financial operations."
            """
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The user's question that requires advanced processing by the chatbot backend"
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
