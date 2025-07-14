# redis_client.py

from redis import Redis
import ssl
from config.config import REDIS_CONFIG
from monitoring.logger.logger import Logger

# Initialize logger
log = Logger()

class RedisConnector:
    """
    A class to manage Redis connections for different environments (dev, uat, prod).
    This class handles the connection setup and provides a method to retrieve the Redis client.
    """
    # Initialize the Redis client based on the environment configuration
    def __init__(self, env="dev"):
        config = REDIS_CONFIG.get(env)
        if not config:
            log.error(f"Invalid Redis environment: {env}. Available options are {list(REDIS_CONFIG.keys())}.")
            raise ValueError(f"Invalid Redis environment: {env}")
        self.redis = self._connect(config)
        log.info(f"Connected to Redis at {config['host']} in {env} environment.")

    # Connect to Redis using the provided configuration
    def _connect(self, config):
        """
        Args:
            config (dict): A dictionary containing Redis connection parameters:
                - host (str): Redis server hostname or IP address
                - port (int): Redis server port
                - key (str): Authentication password/key for Redis
        Returns:
            Redis: An initialized Redis client connection
        Note:
            SSL is enabled with certificate verification disabled (for development use only).
            All responses are automatically decoded to strings.
        """

        log.info("Connecting to Redis...")
        redis = Redis(
                        host=config["host"],
                        port=config["port"],
                        password=config["key"],         # Use the auth key here
                        ssl=True,
                        ssl_cert_reqs=ssl.CERT_NONE,  # Disable cert verification for local/dev
                        decode_responses=True
                    )

        log.info("Redis connection established successfully.")
        
        return redis 

    # get the Redis client instance
    def get_client(self):
        return self.redis
