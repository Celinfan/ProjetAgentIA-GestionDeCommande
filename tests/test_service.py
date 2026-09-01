import pytest

from app.conversation import ConversationMemory
from app.service import OrderService

from app.models import Order, Product

class FakeLLM:
    """LLM simulé pour les tests du service."""

    def __init__(self, decision: dict) -> None: 
        self.decision = decision

    def decide( 
            self, 
            messages: list[dict[str, str]], 
            order_state: dict, 
            expected_field: str | None = None, 
    ) -> dict: 
        return self.decision

def make_service(decision: dict) -> OrderService: 
    """Crée un service utilisant un LLM simulé.""" 
    memory = ConversationMemory() 
    return OrderService( 
        llm=FakeLLM(decision), 
        memory=memory,
    )

def test_customer_and_email_are_saved() -> None: 
    decision = { 
        "actions": [ 
            { 
                "action": "SET_CUSTOMER", 
                "customer": "Alice", 
            }, 
            { 
                "action": "SET_EMAIL", 
                "email": "alice@example.com", 
            }, 
        ]
    } 
    service = make_service(decision) 

    result = service.process_message( "Je suis Alice, alice@example.com" ) 
    assert result["status"] == "NEED_INFORMATION" 
    assert result["order"]["customer"] == "Alice" 
    assert result["order"]["email"] == "alice@example.com"

def test_product_is_added() -> None: 
    decision = { 
        "actions": [ 
            { 
                "action": "SET_CUSTOMER", 
                "customer": "Alice", 
            }, 
            { 
                "action": "SET_EMAIL", 
                "email": "alice@example.com", 
            }, 
            { 
                "action": "ADD_PRODUCT", 
                "name": "Lampes", 
                "unit_price": 10, "quantity": 3, 
            }, 
        ] 
    } 
    service = make_service(decision) 

    result = service.process_message( "Je commande 3 lampes à 10 euros." ) 
    assert result["status"] == "accepted" 
    assert result["total"] == 30.0 
    assert result["action"] == "SEND_CONFIRMATION_EMAIL"

@pytest.mark.parametrize( 
    ("unit_price", "quantity", "expected_status", "expected_action"), 
    [ 
        (10, 1, "rejected", "REJECT_ORDER"), 
        (20, 1, "accepted", "SEND_CONFIRMATION_EMAIL"), 
        (100, 1, "accepted", "SEND_CONFIRMATION_EMAIL"), 
        (500, 1, "accepted", "SEND_CONFIRMATION_EMAIL"), 
        (501, 1, "accepted", "SEND_SUPPLIER_EMAIL"), 
    ], 
) 
def test_business_rules( 
    unit_price: float, 
    quantity: int, 
    expected_status: str, 
    expected_action: str, 
) -> None: 
    decision = { 
        "actions": [ 
            { 
                "action": "SET_CUSTOMER", 
                "customer": "Alice", 
            }, 
            { 
                "action": "SET_EMAIL", 
                "email": "alice@example.com", 
            }, 
            { 
                "action": "ADD_PRODUCT", 
                "name": "Produit test", 
                "unit_price": unit_price, 
                "quantity": quantity, 
            },
        ] 
    } 
    service = make_service(decision) 

    result = service.process_message("Commande test") 
    assert result["status"] == expected_status 
    assert result["action"] == expected_action 
    assert result["total"] == unit_price * quantity 

def test_invalid_email_is_rejected() -> None: 
    decision = { 
        "actions": [ 
            { 
                "action": "SET_CUSTOMER", 
                "customer": "Alice",
            }, 
            { 
                "action": "SET_EMAIL", 
                "email": "pas-un-email", 
            }, 
        ] 
    } 
    service = make_service(decision) 

    result = service.process_message("Alice, pas-un-email") 
    assert result["status"] == "NEED_INFORMATION" 
    assert result["order"]["customer"] == "Alice" 
    assert result["order"]["email"] is None
  
