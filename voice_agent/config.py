import os
from dotenv import load_dotenv

load_dotenv()

AZURE_RTOPENAI_RESOURCE     = os.getenv("AZURE_RTOPENAI_RESOURCE")
AZURE_RTOPENAI_DEPLOYMENT   = os.getenv("AZURE_RTOPENAI_DEPLOYMENT")
AZURE_RTOPENAI_API_VERSION  = os.getenv("AZURE_RTOPENAI_API_VERSION")
AZURE_RTOPENAI_KEY          = os.getenv("AZURE_RTOPENAI_KEY")

AZURE_WS_URL = (
    f"wss://{AZURE_RTOPENAI_RESOURCE}/openai/realtime"
    f"?deployment={AZURE_RTOPENAI_DEPLOYMENT}&api-version={AZURE_RTOPENAI_API_VERSION}"
)
