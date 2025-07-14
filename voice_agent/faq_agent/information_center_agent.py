
from langchain_community.retrievers.bedrock import AmazonKnowledgeBasesRetriever
from .config import (
    AWS_KB_ID,
    AWS_KB_RETRIVAL_CONFIG,
    AWS_REGION,
    AWS_GUARDRAIL_CONFIG
)
import traceback
from logger import logger

log = logger

def faq_knowledge_base(question: str) -> str:
    """
    Retrieve relevant information from the FAQ knowledge base.
    
    This tool searches the AWS knowledge base for answers about wealth management, stock market trading,
    financial regulations, account procedures, and platform features. Use it for questions about
    financial policies, trading rules, and account management.
    
    TYPICAL FAQ EXAMPLES:
    - "What is SPEED-e of NSDL?"
    - "Are existing client details mandatory to mention on given modification form?"
    - "Can a demat account be opened if a trading or commodity account exists?"
    - "Do i need to give documents if I am KRA registered?"
    - "What is Physical Settlement in EQ-Derivatives?"
    - "Why does the session get expired?"
    
    Args:
        question (str): User's natural language question about financial processes or policies.
    
    Returns:
        str: Relevant information from the knowledge base or a fallback message.
    """
    try:
        retriever = AmazonKnowledgeBasesRetriever(
            knowledge_base_id=AWS_KB_ID,
            retrieval_config=AWS_KB_RETRIVAL_CONFIG,
            region_name=AWS_REGION,
        )
        
        log.info(f"FAQ Tool: Asking '{question}'")
        
        # Use the synchronous get_relevant_documents method
        documents = retriever.get_relevant_documents(question)
        
        if not documents:
            return "I couldn't find specific information about that topic in our knowledge base. Could you please rephrase your question or contact our support team for more detailed assistance?"
        
        # Combine the retrieved documents
        response = ""
        for doc in documents:
            response += doc.page_content + "\n\n"
        
        response = response.strip()
        
        log.info(f"FAQ Tool: Got {len(documents)} documents, returning: {response[:200]}...")
        
        return response
        
    except Exception as e:
        log.error(f"FAQ Tool error: {e}")
        log.error(f"Traceback: {traceback.format_exc()}")
        return "I'm experiencing some technical difficulties. Please try rephrasing your question or contact our support team for assistance."