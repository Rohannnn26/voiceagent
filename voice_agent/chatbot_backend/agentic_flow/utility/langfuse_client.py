
from langfuse import Langfuse


from config.config import LANGFUSE_CONFIG , env
from monitoring.logger.logger import Logger

# Initialize logger
log = Logger()

# Initialize Langfuse client
try:
    langfuse = Langfuse(
        public_key=LANGFUSE_CONFIG["LANGFUSE_PUBLIC_KEY"],
        secret_key=LANGFUSE_CONFIG["LANGFUSE_SECRET_KEY"],
        host=LANGFUSE_CONFIG["LANFUSE_HOST"],
        environment=env  # or "production" based on your environment
    )
    log.info("Langfuse client initialized successfully")
except Exception as e:
    log.error(f"Failed to initialize Langfuse client: {str(e)}")