# API FastAPI
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.llm import OllamaLLM
from app.service import OrderService
from app.core.logging_config import setup_logging
import logging
from pydantic import BaseModel
from app.conversation import ConversationMemory

app = FastAPI(title="ProjetAgentIA - GestionDeCommande")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # pratique pour notre développement local, en prod on autoriserait uniquement l'origine de notre frontend 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
memory = ConversationMemory()
service = OrderService(OllamaLLM(), memory)

setup_logging()
logger = logging.getLogger("main")

class ConversationRequest(BaseModel):
    conversation_id: str | None = None
    text: str

@app.get("/health")
def health()-> dict:
    return {"status":"ok"}

@app.post("/orders")
def process_order(request: ConversationRequest) -> dict:
    try:
        return service.process_message(request.text, request.conversation_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
