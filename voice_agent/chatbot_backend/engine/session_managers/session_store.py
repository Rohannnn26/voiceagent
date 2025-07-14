# engine/session/session_store.py

import json
import redis
from engine.session_managers.redis_client import RedisConnector
from datetime import timedelta
from typing import Optional
from config.config import ENV
from monitoring.logger.logger import Logger

# Initialize logger
log = Logger()

class RedisSessionStore:
    """
    Provides a Redis-backed storage engine for managing chatbot session data.
    
    Handles save/load/delete operations with expiration (TTL) support.
    """

    def __init__(self, url: str, ttl_minutes: int = 60):
        """
        Initialize the Redis client and session TTL settings.

        Args:
            url (str): Redis connection URL (e.g., "redis://localhost:6379/0").
            ttl_minutes (int): Time-to-live for session data in minutes.
        """
        log.info(f"Initializing RedisSessionStore.")
        self.redis = redis.from_url(url)  # Connect to Redis using the given URL
        #self.redis = RedisConnector(env=ENV).get_client()
        self.ttl = timedelta(minutes=ttl_minutes)  # Default TTL for session expiration
        log.info("RedisSessionStore initialized successfully.")

    def save(self, session_id: str, data: dict):
        """
        Save session data with expiration to Redis.

        Args:
            session_id (str): Unique session key.
            data (dict): Data to be stored (must be JSON serializable).
        """
        payload = json.dumps(data, default=str)  # Convert to JSON string
        self.redis.setex(session_id, int(self.ttl.total_seconds()), payload)  # Save with expiry

    def load(self, session_id: str) -> Optional[dict]:
        """
        Load a session's data from Redis.

        Args:
            session_id (str): Session key.

        Returns:
            Optional[dict]: The decoded session data, or None if not found.
        """
        raw = self.redis.get(session_id)
        log.info(f"Loading session data for ID: {session_id}, found: {'Yes' if raw else 'No'}")
        return json.loads(raw) if raw else None

    def delete(self, session_id: str):
        """
        Delete a session from Redis.

        Args:
            session_id (str): The session key to remove.
        """
        self.redis.delete(session_id)

    def list_keys(self) -> list:
        """
        List all session keys currently stored in Redis.

        Returns:
            list: A list of session keys as strings.
        """
        return [key.decode() for key in self.redis.keys('*')]  # Convert bytes to strings
