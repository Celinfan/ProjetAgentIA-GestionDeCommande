# actions que l'agent peut demander
import re
from app.order_state import OrderStateManager


class OrderTools:

    def __init__(
        self,
        state_manager: OrderStateManager,
    ):
        self.state_manager = state_manager

    def set_customer(
        self,
        conversation_id: str,
        customer: str,
    ) -> dict:

        self.state_manager.set_customer(
            conversation_id,
            customer,
        )

        return {
            "success": True,
            "field": "customer",
            "value": customer,
        }

    def set_email(
        self,
        conversation_id: str,
        email: str,
    ) -> dict:

        if not self._is_valid_email(email):
            return {
                "success": False,
                "error": "Adresse email invalide.",
            }

        self.state_manager.set_email(
            conversation_id,
            email,
        )

        return {
            "success": True,
            "field": "email",
            "value": email,
        }

    def add_product(
        self,
        conversation_id: str,
        name: str,
        unit_price: float,
        quantity: int,
    ) -> dict:

        if quantity <= 0:
            return {
                "success": False,
                "error": "La quantité doit être supérieure à zéro.",
            }

        if unit_price <= 0:
            return {
                "success": False,
                "error": "Le prix doit être supérieur à zéro.",
            }

        self.state_manager.add_product(
            conversation_id,
            name,
            unit_price,
            quantity,
        )

        return {
            "success": True,
            "product": {
                "name": name,
                "unit_price": unit_price,
                "quantity": quantity,
            },
        }

    def get_order_state(
        self,
        conversation_id: str,
    ) -> dict:

        state = self.state_manager.get_state(
            conversation_id
        )

        return state.model_dump()

    @staticmethod
    def _is_valid_email(email: str) -> bool:

        pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

        return bool(
            re.match(pattern, email)
        )