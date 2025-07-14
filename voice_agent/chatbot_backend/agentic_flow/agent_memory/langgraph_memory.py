

from langchain_community.embeddings import BedrockEmbeddings
from langchain_community.vectorstores import Chroma
from mem0 import Memory

embedding_model = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1")

vector_store = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embedding_model,
    collection_name="mem0"  # Required collection name for Mem0
)


config = {
    "vector_store": {
        "provider": "langchain",
        "config": {
            "vector_store": vector_store
        }
    },
    "embedding_model": {
        "provider": "bedrock",
        "config": {
            "model_id": "amazon.titan-embed-text-v1"
        }
    },
    "version": "v1.1"
}

mem_memory = Memory.from_config(config)
