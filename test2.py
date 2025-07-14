"""
Azure GPT-4o Realtime demo with conversation-item function calling.
Adds `fetch_page_content` so the model can pull full text from any URL
and then answer arbitrary questions about it.
"""
import os, json, asyncio, base64, logging, datetime, textwrap, requests, bs4, websockets, pyaudio
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

# ── 1 Logging ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("realtime-fc")

# ── 2 Env & WS URL ───────────────────────────────────────
load_dotenv(override=True)

RESOURCE   = os.environ["AZURE_RTOPENAI_RESOURCE"].strip().removeprefix("https://").rstrip("/")
DEPLOYMENT = os.environ["AZURE_RTOPENAI_DEPLOYMENT"].strip()
API_KEY    = os.environ["AZURE_RTOPENAI_KEY"].strip()
API_VER    = os.getenv("AZURE_RTOPENAI_API_VERSION", "2025-04-01-preview").strip()

WS_URL = (
    f"wss://{RESOURCE}/openai/realtime"
    f"?deployment={DEPLOYMENT}&api-version={API_VER}"
)

# ── 3 Audio constants ────────────────────────────────────
RATE, CHUNK_MS = 24_000, 100      # 24 kHz, 100 ms
CHUNK = int(RATE * CHUNK_MS / 1000)

# ── 4 Local tool implementations ─────────────────────────
def get_time(city: str) -> dict:
    """Return IST time, regardless of requested city (demo)."""
    now_ist = datetime.datetime.now(ZoneInfo("Asia/Kolkata"))
    return {"time": f"It is {now_ist:%H:%M} IST in {city}."}

def search_docs(query: str) -> dict:
    return {"answer": f"(stub) Top hit for “{query}”…"}

MAX_CHARS = 16_000                # ≈ 10 k tokens – safe for GPT-4o

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

TOOLS = {
    "get_time":            get_time,
    "search_docs":         search_docs,
    "fetch_page_content":  fetch_page_content,
}

FUNCTION_SCHEMAS = [
    {
        "type": "function",
        "name": "get_time",
        "description": "Get the current time in a city.",
        "parameters": {
            "type": "object",
            "properties": { "city": { "type": "string" } },
            "required": ["city"]
        },
    },
    {
        "type": "function",
        "name": "search_docs",
        "description": "Search internal FAQs and documents.",
        "parameters": {
            "type": "object",
            "properties": { "query": { "type": "string" } },
            "required": ["query"]
        },
    },
    {
        "type": "function",
        "name": "fetch_page_content",
        "description": "Download a web page and return all visible text.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": { "type": "string",
                         "description": "Fully-qualified http/https URL" }
            },
            "required": ["url"]
        },
    },
]

# ── 5 Helpers ────────────────────────────────────────────
async def send_response_create(ws):
    await ws.send(json.dumps({
        "type": "response.create",
        "response": {
            "modalities": ["text", "audio"],
            "voice": "alloy"
        }
    }))

def build_fn_output_item(call_id: str, result: dict) -> dict:
    return {
        "type": "conversation.item.create",
        "item": {
            "type": "function_call_output",
            "call_id": call_id,
            "output": json.dumps(result)
        }
    }

# ── 6 Main coroutine ─────────────────────────────────────
async def main():
    async with websockets.connect(
        WS_URL,
        additional_headers={
            "api-key": API_KEY,
            "OpenAI-Beta": "realtime=v1"
        },
        max_size=None, max_queue=None, ping_interval=None
    ) as ws:
        log.info("🔗 Connected → %s", WS_URL)

        # declare tools
        await ws.send(json.dumps({
            "type": "session.update",
            "session": {
                "tools": FUNCTION_SCHEMAS,
                "tool_choice": "auto"
            }
        }))

        # audio setup
        pa  = pyaudio.PyAudio()
        mic = pa.open(format=pyaudio.paInt16, channels=1, rate=RATE,
                      input=True, frames_per_buffer=CHUNK)
        spk = pa.open(format=pyaudio.paInt16, channels=1, rate=RATE, output=True)

        async def pump_mic():
            log.info("🎙️  Mic streaming …")
            while True:
                pcm = mic.read(CHUNK, exception_on_overflow=False)
                await ws.send(json.dumps({
                    "type": "input_audio_buffer.append",
                    "audio": base64.b64encode(pcm).decode()
                }))
                await asyncio.sleep(CHUNK_MS / 1000)

        async def handle_events():
            async for raw in ws:
                msg = json.loads(raw)
                t   = msg["type"]

                if t == "conversation.item.input_audio_transcription.completed":
                    log.info("📝 USER: %s", msg["text"])
                    await send_response_create(ws)

                elif t == "response.audio.delta":
                    spk.write(base64.b64decode(msg["delta"]))
                elif t == "response.text":
                    print(msg["text"], end="", flush=True)

                elif t == "response.done":
                    outs = msg["response"]["output"]
                    if outs and outs[0]["type"] == "function_call":
                        fc       = outs[0]
                        name     = fc["name"]
                        call_id  = fc["call_id"]
                        args     = json.loads(fc["arguments"])
                        log.info("📞 Function call → %s  args=%s", name, args)

                        try:
                            result = TOOLS[name](**args)
                        except Exception as e:
                            result = {"error": str(e)}
                            log.exception("Tool %s failed", name)

                        await ws.send(json.dumps(
                            build_fn_output_item(call_id, result)
                        ))
                        log.info("↩️  function_call_output sent")

                        await send_response_create(ws)
                    else:
                        print()  # newline
                        log.info("✅ Assistant turn complete")

        await asyncio.gather(pump_mic(), handle_events())

if __name__ == "__main__":
    asyncio.run(main())
