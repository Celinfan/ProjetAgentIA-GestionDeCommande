from enum import Enum
from app.models import Order

class Action(str, Enum):
    REJECT_ORDER = "REJECT_ORDER"
    SEND_CONFIRMATION_EMAIL = "SEND_CONFIRMATION_EMAIL"
    SEND_SUPPLIER_EMAIL = "SEND_SUPPLIER_EMAIL"

class OrderService:
    """Le métier reste déterministe : le LLM extrait seulement les données."""

    MINIMUM_AMOUNT = 20.0
    SUPPLIER_THRESHOLD = 500.0

    def __init__(self, llm):
        self.llm = llm

    def parse_order(self, text: str) -> Order:
        data = self.llm.extract_order(text)
        return Order.model_validate(data)

    def process_order(self, order: Order) -> dict:
        total = order.total

        if total < self.MINIMUM_AMOUNT:
            action, status, reason = (
                Action.REJECT_ORDER, "rejected",
                "Montant inférieur au minimum autorisé.",
            )
        elif total > self.SUPPLIER_THRESHOLD:
            action, status, reason = (
                Action.SEND_SUPPLIER_EMAIL, "accepted",
                "Commande importante nécessitant un traitement fournisseur.",
            )
        else:
            action, status, reason = (
                Action.SEND_CONFIRMATION_EMAIL, "accepted",
                "Commande standard.",
            )

        return {
            "status": status,
            "action": action.value,
            "order_id": order.id,
            "customer": order.customer,
            "email": str(order.email),
            "total": round(total, 2),
            "reason": reason,
        }

    def process_text(self, text: str) -> dict:
        order = self.parse_order(text)
        return self.process_order(order)
