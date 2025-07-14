# tracing/langfuse_handler.py
from langfuse import Langfuse
from langfuse.decorators import observe
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv(dotenv_path="../../.env")

# Initialize Langfuse
langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST")
)

@observe()
def run_with_tracing(agent, user_input):
    return agent.run(user_input)
