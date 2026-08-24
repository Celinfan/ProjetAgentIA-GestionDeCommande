from fastapi import FastAPI
from app.models import Order
from app.llm import LLM
from app.service import OrderService

app=FastAPI(title="Order Agent IA - V2")
service=OrderService(); llm=LLM()

@app.get("/health")
async def health(): return {"status":"ok"}

@app.post("/orders")
async def process_order(order: Order):
    result=await service.process(order,llm)
    return {"order_id":order.id,"total":order.total,**result}
