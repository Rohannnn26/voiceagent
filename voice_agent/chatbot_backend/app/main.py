#app/main.py

from fastapi import FastAPI
from app.api.v1.chatbot_routes import router as chatbot_router

app = FastAPI(title="Chatbot API", version="1.0")

app.include_router(chatbot_router, prefix="/api/v1", tags=["Chatbot"])
