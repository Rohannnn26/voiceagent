# chatbot_backend/config/config.py
from dotenv import load_dotenv
import os
from pathlib import Path
from config.secrets import get_secret

load_dotenv()

# Load environment variables from .env file
# env = 'dev'
env =  os.getenv('env', 'dev')  # Default to 'dev' if not set 

secrets = get_secret(env)
# Default JSON flow node
DEFAULT_NODE_CLIENT =  "initial_client"
DEFAULT_NODE_PARTNER =  "initial_partner"
PARTNER_IDS = ["SUBBROKER"]
PARTNER_RQD_CLIENT_ID = ["ledger_report","profit_and_loss_statement","my_details","dp_statement","brokerage_report",
"itr_statement","grandfather_pnl","available_margin","my_dashboard","tds_certificate","stt_ctt_certificate","emodification","markets_research_partner",
"upcoming_buyback","mf_status","fund_payout_status","fund_transfer_status","margin_shortage","new_account_opening","ipo","sauda_details", "digi_cmr","acount_modification_status","contract_note",
"dis_drf_status"]
# JSON file for the flow definition
JSON_FILE_PATH = "flows/deterministic/deterministic_flow_v2.json"
TEST_FILE_PATH = "flows/deterministic/test_flow.json"
ROOT_DISPLAY_INCREMENT = 5
# Redis configuration
REDIS_CONFIG = {
        "host": secrets["valkey_host"],
        "port": secrets["valkey_port"],
        "key": secrets["valkey_key"],  # Use the auth key here
}

# Get environment or default to dev for local development
REDIS_URL = "redis://localhost:6379/0"
REDIS_TTL_MINUTES = 30


# BASE_URL_CONFIG = "http://cs.motilaloswaluat.com/gw/api/cbot"

# pick from secrets
BASE_URL_CONFIG = secrets["base_url_api"]

# Agentic config form here:
AWS_REGION="ap-south-1"
# AWS_KB_ID="EMHQQ3JZUV"
AWS_KB_ID = secrets["aws_kb_id"]
AWS_KB_RETRIVAL_CONFIG={"vectorSearchConfiguration": {"numberOfResults": 2}}
AWS_GUARDRAIL_CONFIG= {"guardrailIdentifier":"weg4no7uwti6","guardrailVersion":"DRAFT"}

SUPERVISOR_MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"
SUPERVISOR_MODEL_ID_DEMO = "anthropic.claude-3-sonnet-20240229-v1:0"
SUPERVISOR_MODEL_KWARGS = {
                "temperature": 0,
                "max_tokens": 1024,
                "anthropic_version": "bedrock-2023-05-31",
                "top_p": 0.1
            }

# Base path for schema files
SCHEMA_DIR = Path("agentic_flow") / "openapi_schema"

# Define all schema paths
ACCOUNT_OPENAPI_SCHEMA_PATH = str(SCHEMA_DIR / "account_agent_schema.json")
ACCOUNT_OPENAPI_STATIC_DATA = str(SCHEMA_DIR / "account_agent_static_data.json")
INFORMATION_CENTRE_OPENAPI_SCHEMA_PATH = str(SCHEMA_DIR / "information_centre_agent_schema.json")
INFORMATION_CENTRE_OPENAPI_STATIC_DATA = str(SCHEMA_DIR / "information_centre_agent_static_data.json")
FUND_OPENAPI_SCHEMA_PATH = str(SCHEMA_DIR / "fund_agent_schema.json")
TRADING_OPENAPI_SCHEMA_PATH = str(SCHEMA_DIR / "trading_agent_schema.json")
PLAN_EXECUTE_OPENAPI_SCHEMA_PATH = str(SCHEMA_DIR / "combine.json")
REPORT_OPENAPI_SCHEMA_PATH = str(SCHEMA_DIR / "report_agent_schema.json")

SYSTEM_PARAMS_MAPPER_PATH = str(SCHEMA_DIR / "system_params_mapper.json")
# PostgreSQL Configuration
db_config = {
    "aurora_host": secrets["aurora_host"],
    "aurora_user": secrets["aurora_user"],
    "aurora_pw": secrets["aurora_pw"],
    "aurora_db": secrets["aurora_db"],
    "aurora_port": secrets["aurora_port"],
    
}


LANGFUSE_CONFIG = {
        "LANGFUSE_PUBLIC_KEY": secrets["LANGFUSE_PUBLIC_KEY"],
        "LANGFUSE_SECRET_KEY": secrets["LANGFUSE_SECRET_KEY"],
        "LANFUSE_HOST": secrets["LANFUSE_HOST"]
}

connection_kwargs = {
    "autocommit": True,
    "prepare_threshold": 0,
}
# PostgreSQL Configuration

# Build PostgreSQL URI
DB_URI = f"postgresql://{db_config['aurora_user']}:{db_config['aurora_pw']}@" \
         f"{db_config['aurora_host']}:{db_config['aurora_port']}/" \
         f"{db_config['aurora_db']}"
