import boto3
from langchain_aws import ChatBedrockConverse

from config.config import AWS_REGION, SUPERVISOR_MODEL_ID_DEMO, AWS_GUARDRAIL_CONFIG
from monitoring.logger.logger import Logger
from langchain_core.messages.utils import (
    trim_messages, 
    count_tokens_approximately
)
# Initialize logger
log = Logger()

# Initialize Bedrock client
bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)

# Instantiate the LLM model from Bedrock
def get_llm_model(model_id=None):
    """
    Returns a ChatBedrockConverse model instance with the specified model ID.
    If no model ID is provided, uses the default model ID.
    
    Args:
        model_id (str, optional): The model ID to use. Defaults to SUPERVISOR_MODEL_ID_DEMO.
    
    Returns:
        ChatBedrockConverse: An instance of the ChatBedrockConverse model.
    """
    if model_id is None:
        model_id = SUPERVISOR_MODEL_ID_DEMO
        log.info(f"Using default model ID: {model_id}")
    else:
        log.info(f"Using specified model ID: {model_id}")
        
    log.info("Initializing ChatBedrockConverse model")
    model = ChatBedrockConverse(
        model=model_id,
        temperature=0,
        max_tokens=None,
        # guardrail_config = AWS_GUARDRAIL_CONFIG,
        # guardrail_config = AWS_GUARDRAIL_CONFIG,
        client=bedrock_client
    )
    log.info("ChatBedrockConverse model initialized successfully")
    return model

def pre_model_hook(messages):
    log.info(f"max tokens till now: {count_tokens_approximately(messages)}")
    trimmed_messages = trim_messages(
        messages,
        strategy="last",
        token_counter=count_tokens_approximately,
        max_tokens= 8000,
        start_on="human",
        end_on=("human", "tool"),
    )
    # Log the trimmed messages for debugging
    return trimmed_messages
