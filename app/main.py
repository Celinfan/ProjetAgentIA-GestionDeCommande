from fastapi import FastAPI, HTTPException
from app.llm import OllamaLLM
from app.service import OrderService
from app.core.logging_config import setup_logging
import logging

app = FastAPI(title="ProjetAgentIA - GestionDeCommande")
service = OrderService(OllamaLLM())

setup_logging()
logger = logging.getLogger("main")


from pydantic import BaseModel
class OrderRequest(BaseModel):
    text: str

@app.get("/health")
def health()-> dict:
    return {"status":"ok"}

@app.post("/orders")
def process_order(order: OrderRequest) -> dict:
    try:
        return service.process_text(order.text)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
