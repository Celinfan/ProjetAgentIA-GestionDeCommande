from app.models import Order

class OrderService:
    """La logique métier reste déterministe; le LLM ne déclenche pas directement une action."""
    async def process(self, order: Order, llm) -> dict:
        try:
            decision=(await llm.classify_order(order)).get("decision")
        except Exception as exc:
            return {"status":"manual_review","reason":f"LLM unavailable: {exc}"}

        if decision == "REJECT":
            return {"status":"rejected","action":"REJECT_ORDER","reason":"Montant inférieur au minimum autorisé."}
        if decision == "SUPPLIER_EMAIL":
            return {"status":"processed","action":"SEND_TO_SUPPLIER","email":"sent","reason":"Commande importante."}
        if decision == "EMAIL":
            return {"status":"processed","action":"SEND_EMAIL","reason":"Commande standard."}
        return {"status":"manual_review","reason":"Decision LLM inconnue."}
