# chatbot_backend/config/config.py
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

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
    "dev": {
        "host": "master.mofsl-chatbot-dev-valkey.xfjxmr.aps1.cache.amazonaws.com",
        "port": 6379,
        "key": "CHat>0Tvalkey4321",  # Use the auth key here
    },
    "uat": {
        "host": "master.mofsl-chatbot-dev-valkey.xfjxmr.aps1.cache.amazonaws.com",
        "port": 6379,
        "key": "CHat>0Tvalkey4321",
    },
    "prod": {
        "host": "master.mofsl-chatbot-dev-valkey.xfjxmr.aps1.cache.amazonaws.com",
        "port": 6379,
        "key": "CHat>0Tvalkey4321",
    }
}

# Get environment or default to dev for local development
ENV =  "dev"
REDIS_URL = "redis://localhost:6379/0"
REDIS_TTL_MINUTES = 30

BASE_URL = "http://10.167.203.119/gw/api"


# Agentic config form here:
AWS_REGION="ap-south-1"
AWS_KB_ID="P3TSMH4AJN"
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
    "dev": {
        "aurora_host": "mofsl-bnd-dev-datamart-provisioned-cluster.cluster-chv7khybxrbp.ap-south-1.rds.amazonaws.com",
        "aurora_user": "datamart_dev",
        "aurora_pw": "Datamart-#Dev#123",
        "aurora_db": "mofirst",
        "aurora_port": "5432",
    }
}

connection_kwargs = {
    "autocommit": True,
    "prepare_threshold": 0,
}
# PostgreSQL Configuration
env = 'dev'
# Build PostgreSQL URI
DB_URI = f"postgresql://{db_config[env]['aurora_user']}:{db_config[env]['aurora_pw']}@" \
         f"{db_config[env]['aurora_host']}:{db_config[env]['aurora_port']}/" \
         f"{db_config[env]['aurora_db']}"

# Langfuse configuration
LANGFUSE_PUBLIC_KEY="pk-lf-1521bfb0-a89c-4f21-8f39-b3ae12fc04d2"
LANGFUSE_SECRET_KEY="sk-lf-46deaf4a-a8d7-4bb2-9ad6-66e604780d67"
LANFUSE_HOST="https://langfuse.motilaloswal.cloud"