import json
import httpx

class LLM:
    def __init__(self, model="qwen2.5:3b-instruct", base_url="http://localhost:11434"):
        self.model=model; self.url=f"{base_url.rstrip('/')}/api/chat"

    async def classify_order(self, order) -> dict:
        prompt=f"""Analyse cette commande. Choisis une seule décision parmi REJECT, EMAIL, SUPPLIER_EMAIL.
Commande: {order.model_dump_json()}
Montant total: {order.total:.2f} EUR
Règles: montant < 20 => REJECT; montant > 500 => SUPPLIER_EMAIL; sinon => EMAIL. Retourne uniquement {{\"decision\":\"...\"}}."""
        payload={"model":self.model,"messages":[{"role":"user","content":prompt}],"stream":False,"format":"json"}
        async with httpx.AsyncClient(timeout=60) as client:
            r=await client.post(self.url,json=payload); r.raise_for_status()
            return json.loads(r.json()["message"]["content"])
