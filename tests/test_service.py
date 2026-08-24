import pytest
from app.models import Order, Product
from app.service import OrderService

class FakeLLM:
    def __init__(self, decision): self.decision=decision
    async def classify_order(self, order): return {"decision":self.decision}

def order(total):
    return Order(id=1,customer="Alice",email="alice@example.com",products=[Product(id=1,name="Lamp",unit_price=total,quantity=1)])

@pytest.mark.asyncio
async def test_email_decision():
    result=await OrderService().process(order(50),FakeLLM("EMAIL"))
    assert result["action"]=="SEND_EMAIL"

@pytest.mark.asyncio
async def test_reject_decision():
    result=await OrderService().process(order(10),FakeLLM("REJECT"))
    assert result["status"]=="rejected"

@pytest.mark.asyncio
async def test_unknown_decision_is_safe():
    result=await OrderService().process(order(50),FakeLLM("BOGUS"))
    assert result["status"]=="manual_review"

@pytest.mark.asyncio
async def test_llm_failure_is_safe():
    class Broken:
        async def classify_order(self, order): raise RuntimeError("offline")
    result=await OrderService().process(order(50),Broken())
    assert result["status"]=="manual_review"
