# API FastAPI

import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.conversation import ConversationMemory
from app.core.logging_config import setup_logging
from app.llm import OllamaLLM
from app.service import OrderService

# le logger est la première chose à construire !!!
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="ProjetAgentIA - GestionDeCommande")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # pratique pour notre développement local, en prod on autoriserait uniquement l'origine de notre frontend 
    allow_credentials=False, # Pour un développement local, allow_credentials=False est plus cohérent
    allow_methods=["*"],
    allow_headers=["*"],
)

memory = ConversationMemory()
service = OrderService(OllamaLLM(), memory)


class ConversationRequest(BaseModel):
    """Requête envoyée lors d'un échange avec l'assistant."""

    conversation_id: str | None = None
    text: str

@app.get("/health")
def health()-> dict:
    """Vérifie que l'API est disponible."""
    return {"status":"ok"}

@app.post("/orders")
def process_order(request: ConversationRequest) -> dict:
    """Traite une demande de commande."""
    try:
        return service.process_message(request.text, request.conversation_id)
    except Exception as exc:
        logger.exception("Erreur lors du traitement de la commande.")
        raise HTTPException(status_code=400, detail=str(exc)) from exc
