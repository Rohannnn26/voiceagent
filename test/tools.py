import os
import asyncio, base64, logging, datetime, textwrap, bs4, requests
from zoneinfo import ZoneInfo

def get_time(city: str) -> dict:
    """Return IST time, regardless of requested city (demo)."""
    now_ist = datetime.datetime.now(ZoneInfo("Asia/Kolkata"))
    return {"time": f"It is {now_ist:%H:%M} IST in {city}."}

MAX_CHARS = 16_000  # ≈ 10 k tokens – safe for GPT-4o

def fetch_page_content(url: str) -> dict:
    """
    Download a page and return all visible text, clipped to MAX_CHARS.
    The model can then answer any follow-up questions about it.
    """
    try:
        html = requests.get(url, timeout=8,
                            headers={"User-Agent": "Mozilla/5.0"}).text
    except Exception as e:
        return {"error": f"fetch failed: {e}"}

    soup = bs4.BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = " ".join(t.strip() for t in soup.stripped_strings)
    text = textwrap.shorten(text, width=MAX_CHARS,
                            placeholder=" …[truncated]")
    return {"content": text}

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
        "name": "fetch_page_content",
        "description": (
            "Fetch detailed information about any person, place, event, concept, or general topic by downloading "
            "and returning all visible text content from a relevant webpage (e.g., Wikipedia or official source). "
            "Call this tool whenever the user asks questions like 'tell me about...', 'give me details on...', "
            "'who is...', 'what is...', 'where is...', or seeks comprehensive information about anything."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": (
                        "Fully-qualified URL (typically Wikipedia or an authoritative source) related to "
                        "the topic the user asked about."
                    )
                }
            },
            "required": ["url"]
        },
    },

    {
    "type": "function",
    "name": "faq_knowledge_base",
    "description": (
        "Search and return answers from Motilal Oswal's internal FAQ knowledge base "
        "about wealth management, trading, demat procedures, regulations, and account-related issues."
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
}

]

TOOLS = {
    "get_time": get_time,
    "fetch_page_content": fetch_page_content,
}
