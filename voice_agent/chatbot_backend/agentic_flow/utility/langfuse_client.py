
from langfuse import Langfuse


from config.config import LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANFUSE_HOST
from monitoring.logger.logger import Logger

# Initialize logger
log = Logger()

# Initialize Langfuse client
try:
    langfuse = Langfuse(
        public_key=LANGFUSE_PUBLIC_KEY,
        secret_key=LANGFUSE_SECRET_KEY,
        host=LANFUSE_HOST,
        environment="dev"  # or "production" based on your environment
    )
    log.info("Langfuse client initialized successfully")
except Exception as e:
    log.error(f"Failed to initialize Langfuse client: {str(e)}")